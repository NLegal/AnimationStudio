"""Batch generation orchestration for the full universe.

Drives the existing ``GenerationJob`` pipeline (prompt → generate → score →
diversity filter → shortlist) across many catalog seeds: all characters, all
world zones, and all reusable props.  Works with any GenerationBackend:
mock (no hardware), ComfyUI, or a cloud API.

Usage (from scripts):
    runner = BatchRunner(asset_repo, char_repo)
    summary = await runner.run_scope("characters", count=8, shortlist=5)
"""

import asyncio
import logging
from typing import Awaitable, Callable, Optional

from src.generation_engine.base import GenerationBackend
from src.identity_engine.scorer import IdentityScorer
from src.pipeline.diversity_filter import DiversityFilter
from src.pipeline.generation_job import GenerationJob
from src.pipeline.job_queue import Job, JobQueue
from src.prompt_builder.builder import PromptBuilder
from src.prompt_builder.templates import CharacterPrompt, EnvironmentPrompt, PropPrompt
from src.universe.catalog import (
    ART_DIRECTION,
    CharacterSeed,
    EnvironmentSeed,
    PropSeed,
)
from src.universe.seed import (
    build_character_model,
    build_environment_model,
    build_prop_model,
)

logger = logging.getLogger(__name__)

# Default negative prompt for env/prop generation (child-safe world rules).
_DEFAULT_NEGATIVE = (
    "dark, abandoned, dirty, graffiti, broken windows, cracked roads, "
    "realistic decay, horror, weapons, violence, industrial pollution, "
    "low quality, blurry, text, watermark, logo"
)


def resolve_backend(name: str = "mock", comfyui_url: str = "http://localhost:8188",
                    provider: str = "fal", api_key: Optional[str] = None) -> GenerationBackend:
    """Build a GenerationBackend by name (lazy imports keep startup light)."""
    name = (name or "mock").lower()
    if name in ("mock", ""):
        from src.generation_engine.mock_backend import MockBackend
        return MockBackend()
    if name in ("comfy", "comfyui"):
        from src.generation_engine.comfy_backend import ComfyUIBackend
        return ComfyUIBackend(server_url=comfyui_url)
    if name in ("cloud", "cloudapi"):
        from src.generation_engine.cloud_backend import CloudAPIBackend
        return CloudAPIBackend(provider=provider, api_key=api_key)
    raise ValueError(f"Unknown backend '{name}'. Use mock, comfyui, or cloud.")


def build_prompt(seed, kind: str, asset_type: str, variant: str) -> tuple[str, str]:
    """Build a (positive, negative) prompt pair for a catalog seed."""
    if kind == "character":
        outfit = getattr(seed, "default_outfit", "") or "default outfit"
        if asset_type == "outfit":
            # Resolve a wardrobe variant name to its full description so the
            # prompt carries the detail (variant is the clean wardrobe name).
            wardrobe = getattr(seed, "bio_data", {}).get("wardrobe", {})
            description = wardrobe.get(variant, "")
            if not description:
                for _name, desc in wardrobe.items():
                    if variant and (
                        variant.lower() in desc.lower()
                        or desc.lower() in variant.lower()
                    ):
                        description = desc
                        break
            outfit = description or variant or outfit
        prompt = CharacterPrompt(
            name=seed.name,
            species=getattr(seed, "species", ""),
            appearance=getattr(seed, "appearance", ""),
            outfit=outfit,
            style=ART_DIRECTION,
        )
        if asset_type == "lighting":
            return PromptBuilder().build(
                prompt, asset_type="reference", lighting=variant
            )
        return PromptBuilder().build(prompt, asset_type=asset_type, variant=variant)
    if kind == "environment":
        env = EnvironmentPrompt(
            name=getattr(seed, "name", ""),
            description=getattr(seed, "description", "")[:400],
        )
        if asset_type not in (
            "environment", "exterior", "interior", "season",
            "time_of_day", "weather", "camera", "lighting",
        ):
            asset_type = "exterior"
        positive, builder_neg = PromptBuilder().build_environment(
            env, asset_type=asset_type, variant=variant,
        )
        # Fold in zone-specific negatives (e.g. "urban, realistic city").
        zone_neg = getattr(seed, "negative_prompt", "") or ""
        terms = [t for t in (builder_neg, zone_neg)
                 if t and t != _DEFAULT_NEGATIVE]
        negative = ", ".join(terms) if terms else _DEFAULT_NEGATIVE
        return positive, negative
    if kind == "vehicle":
        vehicle = EnvironmentPrompt(
            name=getattr(seed, "name", ""),
            description=getattr(seed, "description", "")[:400],
        )
        return PromptBuilder().build_vehicle(vehicle, variant=variant)
    if kind == "background":
        bg = EnvironmentPrompt(
            name=getattr(seed, "name", ""),
            description=getattr(seed, "description", "")[:400],
        )
        return PromptBuilder().build_background(bg, variant=variant)
    if kind == "prop":
        prop = PropPrompt(
            name=getattr(seed, "name", seed.asset_id),
            description=getattr(seed, "description", ""),
            colors=getattr(seed, "colors", ""),
            material=getattr(seed, "material", ""),
            category=getattr(seed, "category", ""),
        )
        if asset_type not in ("reference", "prop", "view", "material", "color", "lighting"):
            asset_type = "reference"
        return PromptBuilder().build_prop(prop, asset_type=asset_type, variant=variant)
    raise ValueError(f"Unknown seed kind '{kind}'")


class BatchRunner:
    """Runs generation jobs for many catalog seeds against one backend."""

    def __init__(
        self,
        asset_repo,
        char_repo=None,
        backend: Optional[GenerationBackend] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        scorer: Optional[IdentityScorer] = None,
        diversity_filter: Optional[DiversityFilter] = None,
        persist_images: bool = False,
        universe_dir: str = "Universe",
        world_dir: str = "World",
        assets_dir: str = "Assets",
        on_asset: Optional[Callable[[dict], Awaitable]] = None,
    ):
        self.asset_repo = asset_repo
        self.char_repo = char_repo or asset_repo
        self.backend = backend or resolve_backend("mock")
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.scorer = scorer or IdentityScorer()
        self.diversity_filter = diversity_filter or DiversityFilter(n_clusters=5)
        self.job_queue = JobQueue()
        self.persist_images = persist_images
        self.universe_dir = universe_dir
        self.world_dir = world_dir
        self.assets_dir = assets_dir
        self.on_asset = on_asset

    # ------------------------------------------------------------------ #
    #  Character record management
    # ------------------------------------------------------------------ #

    async def ensure_character(self, seed, kind: str) -> Optional[str]:
        """Seed the record for a catalog seed if missing; return its id.

        An existing record is only reused when its category matches the seed
        kind — otherwise a new record is created.  This prevents world
        locations and props that share a display name (e.g. "Pond", "Library")
        from being merged onto the wrong record.
        """
        model = None
        if kind == "character":
            model = build_character_model(seed)  # type: ignore[arg-type]
        elif kind == "environment":
            model = build_environment_model(seed)  # type: ignore[arg-type]
        elif kind in ("prop", "vehicle", "background"):
            model = build_prop_model(seed)  # type: ignore[arg-type]
        if model is None:
            return None

        existing = await self._find_record(model)
        if existing is None:
            try:
                return await self.char_repo.save_character(model)
            except Exception as exc:
                logger.warning("Could not seed '%s': %s", model.name, exc)
                return None

        # Self-heal stale metadata (e.g. category_dir added after the record
        # was first seeded) when reusing an existing record.
        try:
            updater = self.char_repo.update_character
        except (NotImplementedError, AttributeError):
            updater = None
        if updater is not None and getattr(existing, "bio_data", None) != model.bio_data:
            try:
                await updater(existing.id, model)
            except Exception as exc:
                logger.warning("Could not refresh '%s': %s", model.name, exc)

        # Props are keyed by their permanent asset_id — a shared display name
        # (e.g. "banana") must not merge two distinct catalog entries.
        if kind == "prop":
            existing_id = (getattr(existing, "bio_data", None) or {}).get("asset_id", "")
            if existing_id != getattr(seed, "asset_id", ""):
                model.name = f"{model.name} ({seed.asset_id})"
                renamed = await self._find_record(model)
                if renamed is not None:
                    return renamed.id
                try:
                    return await self.char_repo.save_character(model)
                except Exception as exc:
                    logger.warning("Could not seed '%s': %s", model.name, exc)
                    return None
        return existing.id

    async def _find_record(self, model) -> Optional[object]:
        """Look up an existing record, preferring a category-exact match."""
        try:
            return await self.char_repo.find_character_by_name_and_category(
                model.name, model.category
            )
        except (NotImplementedError, AttributeError):
            try:
                return await self.char_repo.find_character_by_name(model.name)
            except (NotImplementedError, AttributeError):
                return None

    async def _has_variant(
        self,
        character_id: str,
        asset_type: str,
        variant: str,
        skip_scored: bool = False,
    ) -> bool:
        """True when this record already owns a usable asset for the variant.

        By default only shortlisted/approved/production assets count, so a
        user can re-run the batch to produce better candidates for a variant
        that was scored but never shortlisted.  Pass ``skip_scored=True`` for
        crash-resume runs (Colab): everything that was generated and synced is
        kept, and nothing is regenerated.
        """
        try:
            existing = await self.asset_repo.find_by_character(
                character_id, asset_type
            )
        except (NotImplementedError, AttributeError):
            return False
        usable = ("shortlisted", "approved", "production")
        if skip_scored:
            usable += ("scored",)
        return any(
            getattr(a, "variant", "") == variant
            and getattr(a, "state", "") in usable
            for a in existing
        )

    # ------------------------------------------------------------------ #
    #  Generation
    # ------------------------------------------------------------------ #

    async def generate_one(
        self,
        seed,
        kind: str,
        count: int = 8,
        shortlist: int = 5,
        asset_type: Optional[str] = None,
        variant: str = "front",
        batch_id: str = "",
        backend: Optional[GenerationBackend] = None,
        skip_scored: bool = False,
    ) -> dict:
        """Generate candidates for a single seed and return its summary."""
        backend = backend or self.backend
        asset_type = asset_type or {
            "character": "reference",
            "environment": "environment",
            "prop": "reference",
            "vehicle": "vehicle",
            "background": "background",
        }[kind]

        character_id = await self.ensure_character(seed, kind)
        if not character_id:
            return {
                "name": getattr(seed, "name", ""),
                "kind": kind,
                "error": "could not create character record",
                "generated": 0,
                "shortlisted": 0,
            }

        # Idempotency: skip variants that already have a usable asset for this
        # record so reruns never duplicate the library (PHASE3.md — "Never
        # create the same object twice").  With skip_scored=True even a scored
        # (but unshortlisted) asset counts, so crash-resume runs keep every
        # image that was generated and synced.
        if await self._has_variant(character_id, asset_type, variant,
                                   skip_scored=skip_scored):
            return {
                "name": getattr(seed, "name", ""),
                "kind": kind,
                "character_id": character_id,
                "asset_type": asset_type,
                "variant": variant,
                "skipped": True,
                "generated": 0,
                "shortlisted": [],
            }

        positive, negative = build_prompt(seed, kind, asset_type, variant)
        job: Job = self.job_queue.create_job(
            character_id=character_id,
            job_type=asset_type,
            config={
                "variants": [{"name": variant, "prompt": positive,
                              "negative_prompt": negative}],
                "count": max(1, count),
                "shortlist_size": max(1, shortlist),
                "batch_id": batch_id,
            },
        )

        generation = GenerationJob(
            backend=backend,
            prompt_builder=self.prompt_builder,
            identity_scorer=self.scorer,
            asset_repo=self.asset_repo,
            diversity_filter=self.diversity_filter,
            char_repo=self.char_repo,
            persist_images=self.persist_images,
            universe_dir=self.universe_dir,
            world_dir=self.world_dir,
            assets_dir=self.assets_dir,
            on_asset=self.on_asset,
        )
        result = await generation.execute(job)

        return {
            "name": getattr(seed, "name", ""),
            "kind": kind,
            "character_id": character_id,
            "job_id": job.id,
            "generated": result["total_generated"],
            "scored": result["total_scored"],
            "shortlisted": result["shortlisted_ids"],
        }

    async def run_seeds(
        self,
        seeds: list,
        kind: str,
        count: int = 8,
        shortlist: int = 5,
        limit: Optional[int] = None,
        jobs: int = 1,
        asset_type: Optional[str] = None,
        variant: str = "front",
        batch_id: str = "",
        backend: Optional[GenerationBackend] = None,
        skip_scored: bool = False,
    ) -> dict:
        """Generate for many seeds concurrently (semaphore-limited)."""
        selected = seeds[:limit] if limit else seeds
        semaphore = asyncio.Semaphore(max(1, jobs))

        async def _guarded(seed) -> dict:
            async with semaphore:
                return await self.generate_one(
                    seed, kind, count=count, shortlist=shortlist,
                    asset_type=asset_type, variant=variant, batch_id=batch_id,
                    backend=backend, skip_scored=skip_scored,
                )

        results = await asyncio.gather(*(_guarded(s) for s in selected))
        summaries = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]

        return {
            "kind": kind,
            "items_attempted": len(selected),
            "items_succeeded": len(summaries),
            "items_failed": len(failed),
            "total_generated": sum(r["generated"] for r in summaries),
            "total_shortlisted": sum(len(r["shortlisted"]) for r in summaries),
            "batch_id": batch_id,
            "failures": failed,
        }

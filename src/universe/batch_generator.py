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
from typing import Optional

from src.generation_engine.base import GenerationBackend
from src.identity_engine.scorer import IdentityScorer
from src.pipeline.diversity_filter import DiversityFilter
from src.pipeline.generation_job import GenerationJob
from src.pipeline.job_queue import Job, JobQueue
from src.prompt_builder.builder import PromptBuilder
from src.prompt_builder.templates import CharacterPrompt
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
        prompt = CharacterPrompt(
            name=seed.name,
            species=getattr(seed, "species", ""),
            appearance=getattr(seed, "appearance", ""),
            outfit=getattr(seed, "default_outfit", "") or "default outfit",
            style=ART_DIRECTION,
        )
        return PromptBuilder().build(prompt, asset_type=asset_type, variant=variant)
    if kind == "environment":
        negative = getattr(seed, "negative_prompt", "") or _DEFAULT_NEGATIVE
        positive = getattr(seed, "prompt", "") or (
            f"Little Learning Town, {seed.name}, {seed.description}, "
            f"{ART_DIRECTION}, masterpiece, 8k"
        )
        return positive, negative
    if kind == "prop":
        name = getattr(seed, "name", seed.asset_id)
        desc = getattr(seed, "description", "")
        colors = getattr(seed, "colors", "")
        details = ", ".join(p for p in (desc, colors) if p)
        base = (
            "single object, product shot, clean background, "
            f"{ART_DIRECTION}, rounded edges, soft shadows, masterpiece, 8k"
        )
        if details:
            positive = f"{name}, {details}, {base}"
        else:
            positive = f"{name}, {base}"
        return positive, _DEFAULT_NEGATIVE
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
    ):
        self.asset_repo = asset_repo
        self.char_repo = char_repo or asset_repo
        self.backend = backend or resolve_backend("mock")
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.scorer = scorer or IdentityScorer()
        self.diversity_filter = diversity_filter or DiversityFilter(n_clusters=5)
        self.job_queue = JobQueue()

    # ------------------------------------------------------------------ #
    #  Character record management
    # ------------------------------------------------------------------ #

    async def ensure_character(self, seed, kind: str) -> Optional[str]:
        """Seed the record for a catalog seed if missing; return its id."""
        model = None
        if kind == "character":
            model = build_character_model(seed)  # type: ignore[arg-type]
        elif kind == "environment":
            model = build_environment_model(seed)  # type: ignore[arg-type]
        elif kind == "prop":
            model = build_prop_model(seed)  # type: ignore[arg-type]
        if model is None:
            return None

        try:
            existing = await self.char_repo.find_character_by_name(model.name)
        except (NotImplementedError, AttributeError):
            existing = None
        if existing is not None:
            return existing.id

        try:
            return await self.char_repo.save_character(model)
        except Exception as exc:
            logger.warning("Could not seed '%s': %s", model.name, exc)
            return None

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
    ) -> dict:
        """Generate candidates for a single seed and return its summary."""
        backend = backend or self.backend
        asset_type = asset_type or {
            "character": "reference",
            "environment": "environment",
            "prop": "prop",
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
    ) -> dict:
        """Generate for many seeds concurrently (semaphore-limited)."""
        selected = seeds[:limit] if limit else seeds
        semaphore = asyncio.Semaphore(max(1, jobs))

        async def _guarded(seed) -> dict:
            async with semaphore:
                return await self.generate_one(
                    seed, kind, count=count, shortlist=shortlist,
                    asset_type=asset_type, variant=variant, batch_id=batch_id,
                    backend=backend,
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

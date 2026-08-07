"""GenerationJob — orchestrates the full generation pipeline for one job.

Wires: prompt → generate → score → diversity filter → save → shortlist.

Each variant in a job goes through the full pipeline. Partial failures
are handled per-variant so one failing variant does not block others.
"""

import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.generation_engine.base import GenerationBackend, GenerationInput
from src.identity_engine.scorer import IdentityScorer
from src.asset_repository.asset_paths import asset_destination, repo_relative_path
from src.asset_repository.interfaces import AssetRepository
from src.models.schemas import AssetModel, CharacterModel
from src.prompt_builder.builder import PromptBuilder
from src.prompt_builder.templates import CharacterPrompt
from src.pipeline.job_queue import Job, JobError
from src.pipeline.diversity_filter import DiversityFilter

logger = logging.getLogger(__name__)

# Default number of images to generate per variant
_DEFAULT_COUNT = 50

# Number of shortlisted assets per variant presented for human review
_DEFAULT_SHORTLIST_SIZE = 5


class GenerationJob:
    """Orchestrates the full generation pipeline for one job.

    Executes the D-04 hybrid pipeline for a single generation job:
    50-100 candidates → technical auto-scoring → diversity filter →
    scored assets saved → top-k shortlisted for human review.

    Usage:
        gj = GenerationJob(backend, prompt_builder, scorer, asset_repo, diversity_filter)
        result = await gj.execute(job)
        print(result['shortlisted_ids'])
    """

    def __init__(
        self,
        backend: GenerationBackend,
        prompt_builder: PromptBuilder,
        identity_scorer: IdentityScorer,
        asset_repo: AssetRepository,
        diversity_filter: Optional[DiversityFilter] = None,
        char_repo: Optional[object] = None,
        persist_images: bool = False,
        universe_dir: str = "Universe",
        world_dir: str = "World",
        assets_dir: str = "Assets",
    ):
        self.backend = backend
        self.prompt_builder = prompt_builder
        self.scorer = identity_scorer
        self.asset_repo = asset_repo
        self.diversity_filter = diversity_filter or DiversityFilter(
            n_clusters=5
        )
        self.char_repo = char_repo
        self.persist_images = persist_images
        self.universe_dir = universe_dir
        self.world_dir = world_dir
        self.assets_dir = assets_dir
        self._rng = random.SystemRandom()

    async def execute(self, job: Job) -> dict:
        """Run the full generation pipeline for a job.

        For each variant in the job config, generates images, scores them,
        applies diversity filtering, saves scored assets, and shortlists
        the top candidates for human review.

        Args:
            job: The Job to execute (status should be 'running').

        Returns:
            Summary dict with keys:
            - total_generated: int
            - total_scored: int
            - shortlisted_ids: list[str]
            - duration: float (seconds)
            - variants_completed: int
            - variants_failed: int

        Raises:
            JobError: If job is in an invalid state or critical resources
                      are missing.
        """
        start_time = time.monotonic()

        if job.status not in ("pending", "running"):
            raise JobError(
                f"Cannot execute job '{job.id}' with status '{job.status}'. "
                "Job must be 'pending' or 'running'."
            )

        job.status = "running"
        variants = job.config.get("variants", [{"name": "front"}])
        count = job.config.get("count", _DEFAULT_COUNT)
        shortlist_size = job.config.get("shortlist_size", _DEFAULT_SHORTLIST_SIZE)

        # Resolve character prompt data
        character = await self._resolve_character(job.character_id)

        summary = {
            "total_generated": 0,
            "total_scored": 0,
            "shortlisted_ids": [],
            "duration": 0.0,
            "variants_completed": 0,
            "variants_failed": 0,
        }

        for variant in variants:
            try:
                variant_result = await self._process_variant(
                    job=job,
                    variant=variant,
                    character=character,
                    count=count,
                    shortlist_size=shortlist_size,
                )
                summary["total_generated"] += variant_result["generated"]
                summary["total_scored"] += variant_result["scored"]
                summary["shortlisted_ids"].extend(variant_result["shortlisted_ids"])
                summary["variants_completed"] += 1
            except Exception as exc:
                logger.warning(
                    "Variant '%s' failed for job '%s': %s",
                    variant.get("name", "unknown"),
                    job.id,
                    exc,
                )
                summary["variants_failed"] += 1

        job.status = "completed"
        job.completed_at = datetime.now()
        summary["duration"] = time.monotonic() - start_time
        return summary

    async def _resolve_character(self, character_id: str) -> Optional[CharacterPrompt]:
        """Resolve character data from the asset repository.

        If the character does not exist in the repo (e.g. test scenarios),
        returns None and generation proceeds with prompt from job config.

        Args:
            character_id: The character identifier.

        Returns:
            CharacterPrompt if character found, None otherwise.
        """
        try:
            char_model = await self.asset_repo.get_character(character_id)
            if char_model is None:
                return None
            return CharacterPrompt(
                name=char_model.name,
                species=getattr(char_model, "species", ""),
                appearance=char_model.bio_data.get("appearance", ""),
                outfit=char_model.bio_data.get("default_outfit", "default outfit"),
            )
        except (AttributeError, NotImplementedError):
            # AssetRepository may not implement get_character
            return None
        except Exception as exc:
            logger.debug("Could not resolve character '%s': %s", character_id, exc)
            return None

    async def _resolve_character_model(self, character_id: str) -> Optional[CharacterModel]:
        """Resolve the full character record (for image persistence paths)."""
        for repo in (self.char_repo, self.asset_repo):
            getter = getattr(repo, "get_character", None)
            if getter is None:
                continue
            try:
                model = await getter(character_id)
                if model is not None:
                    return model
            except Exception:
                continue
        return None

    def _persist_image(
        self,
        img,
        char: CharacterModel,
        asset_type: str,
        variant: str,
        seed: int,
    ) -> str:
        """Write a generated image into the catalog tree; return the stored path.

        Returns a repository-root-relative ``file_path`` (e.g.
        ``Universe/Characters/Lily Bunny/expressions/angry_s123.png``) or an
        empty string when persistence fails so the pipeline continues.
        """
        try:
            destination = asset_destination(
                char.name,
                char.category,
                asset_type,
                variant or "",
                char.bio_data or {},
                self.universe_dir,
                self.world_dir,
                self.assets_dir,
                seed=seed,
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            img.save(destination, format="PNG")
            catalog_root = Path(self.universe_dir).parent
            return repo_relative_path(destination, catalog_root)
        except Exception as exc:
            logger.warning(
                "Could not persist image for %s/%s/%s: %s",
                getattr(char, "name", "?"), asset_type, variant, exc,
            )
            return ""

    async def _process_variant(
        self,
        job: Job,
        variant: dict,
        character: Optional[CharacterPrompt],
        count: int,
        shortlist_size: int,
    ) -> dict:
        """Process a single variant through the full pipeline.

        Args:
            job: The parent job.
            variant: Variant config dict (name, angle, expression, etc.).
            character: Resolved CharacterPrompt (may be None).
            count: Number of images to generate.
            shortlist_size: Number of images to shortlist.

        Returns:
            Dict with keys: generated, scored, shortlisted_ids.
        """
        variant_name = variant.get("name", "front")
        asset_type = job.job_type

        # Resolve the character record once when image persistence is enabled
        # so candidates can be written into the organized catalog tree.
        char = None
        if self.persist_images:
            char = await self._resolve_character_model(job.character_id)

        # 1. Build prompt
        if character is not None:
            positive, negative = self.prompt_builder.build(
                character=character,
                asset_type=asset_type,
                variant=variant_name,
                **variant,
            )
        else:
            # Fallback: use prompt directly from variant config
            positive = variant.get("prompt", variant_name)
            negative = variant.get("negative_prompt", "")

        # 2. Generate N candidates with iterative seeds
        seeds = self._generate_seeds(count)
        all_images = []
        all_seeds = []

        for seed in seeds:
            gen_input = GenerationInput(
                prompt=positive,
                negative_prompt=negative,
                seed=seed,
                num_images=1,
            )
            output = self.backend.generate(gen_input)
            if output.images:
                all_images.extend(output.images)
                all_seeds.append(seed)

        if not all_images:
            logger.warning(
                "No images generated for variant '%s' (job '%s')",
                variant_name,
                job.id,
            )
            return {"generated": 0, "scored": 0, "shortlisted_ids": []}

        # 3. Score all generated images
        scored_assets = []
        for idx, img in enumerate(all_images):
            scores = self.scorer.score_all(img)
            brand = self.scorer.brand_score(img)
            brand_total = brand.get("total", 0.0)

            seed_value = all_seeds[idx] if idx < len(all_seeds) else 0
            file_path = ""
            if self.persist_images and char is not None:
                file_path = self._persist_image(
                    img, char, asset_type, variant_name, seed_value
                )

            asset = AssetModel(
                character_id=job.character_id,
                asset_type=asset_type,
                variant=variant_name,
                state="scored",
                file_path=file_path,
                prompt=positive,
                seed=seed_value,
                model_id="",
                scores=scores,
                brand_score=brand_total,
            )
            # Save to repository
            try:
                asset_id = await self.asset_repo.save(asset)
                asset.id = asset_id
            except Exception as exc:
                logger.warning(
                    "Failed to save scored asset for variant '%s': %s",
                    variant_name,
                    exc,
                )
                # Use a temp ID for diversity filtering
                pass

            scored_assets.append((img, brand_total, asset))

        scored_count = len(scored_assets)

        # 4. Run diversity filter
        images_for_filter = [item[0] for item in scored_assets]
        scores_for_filter = [item[1] for item in scored_assets]

        selected = self.diversity_filter.cluster_and_select(
            images=images_for_filter,
            scores=scores_for_filter,
            n_select=shortlist_size,
        )

        shortlisted_ids = []
        for idx_in_selected, _score in selected:
            _img, _brand, asset = scored_assets[idx_in_selected]
            try:
                await self.asset_repo.update_state(asset.id, "shortlisted")
                shortlisted_ids.append(asset.id)
            except Exception as exc:
                logger.warning(
                    "Failed to shortlist asset '%s': %s",
                    asset.id,
                    exc,
                )

        return {
            "generated": len(all_images),
            "scored": scored_count,
            "shortlisted_ids": shortlisted_ids,
        }

    def _generate_seeds(self, count: int) -> list[int]:
        """Generate a list of unique seeds for image generation.

        Uses random.SystemRandom for cryptographic-quality randomness
        when no seed is specified (T-01-09).

        Args:
            count: Number of seeds to generate.

        Returns:
            List of unique integer seeds.
        """
        seeds: set[int] = set()
        while len(seeds) < count:
            seeds.add(self._rng.randint(0, 2**31 - 1))
        return sorted(seeds)

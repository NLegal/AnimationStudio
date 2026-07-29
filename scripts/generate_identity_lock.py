#!/usr/bin/env python3
"""generate_identity_lock.py — Identity Lock: Multi-angle reference sheet generation for Lily Bunny.

Executes the first stage of the Progressive Locking Pipeline (D-05/D-06):
Identity Lock produces canonical multi-angle reference sheets that define
what "Lily Bunny looks like" for all downstream scoring.

Pipeline: ComfyUIBackend(Flux) → PromptBuilder → IdentityScorer →
          DiversityFilter → SQLiteAssetRepository → human review → Universe Library

Usage:
    python scripts/generate_identity_lock.py

Requires:
    - ComfyUI running at http://localhost:8188 with Flux model installed
    - Python packages: requests, Pillow, scikit-learn (all in pyproject.toml)
"""

import asyncio
import json
import logging
import random
import sys
import time
from pathlib import Path
from typing import Optional

from PIL import Image

from src.generation_engine.base import GenerationInput
from src.generation_engine.comfy_backend import ComfyUIBackend
from src.identity_engine.scorer import IdentityScorer
from src.asset_repository.sqlite_repo import (
    SQLiteAssetRepository,
    SQLiteCharacterRepository,
)
from src.models.schemas import AssetModel, CharacterModel
from src.pipeline.diversity_filter import DiversityFilter
from src.prompt_builder.builder import PromptBuilder
from src.prompt_builder.templates import CharacterPrompt

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHARACTER_NAME = "Lily Bunny"

# Reference angles to generate — each producing a pool of candidates
ANGLES = [
    {"name": "front", "angle": "front", "count": 80, "shortlist_size": 10},
    {"name": "3_4", "angle": "3/4", "count": 80, "shortlist_size": 10},
    {"name": "profile", "angle": "profile", "count": 80, "shortlist_size": 10},
    {"name": "back", "angle": "back", "count": 80, "shortlist_size": 10},
]

# Output directory for approved reference images
UNIVERSE_DIR = Path("Universe/Characters/Lily Bunny/references")

COMFYUI_URL = "http://localhost:8188"
DB_PATH = "catalog.db"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def check_comfyui() -> bool:
    """Verify ComfyUI is reachable at the configured URL."""
    import requests

    try:
        r = requests.get(f"{COMFYUI_URL}/", timeout=5)
        r.raise_for_status()
        print(f"✓ ComfyUI reachable at {COMFYUI_URL}")
        return True
    except Exception as exc:
        print(f"✗ ComfyUI not reachable at {COMFYUI_URL}: {exc}")
        print("  Start ComfyUI first, then re-run this script.")
        return False


def _generate_seeds(count: int) -> list[int]:
    """Generate a list of unique random seeds for image generation."""
    rng = random.SystemRandom()
    seeds: set[int] = set()
    while len(seeds) < count:
        seeds.add(rng.randint(0, 2**31 - 1))
    return sorted(seeds)


# ---------------------------------------------------------------------------
# Wrapper repo that combines character + asset repos for the Review UI
# ---------------------------------------------------------------------------


class _CombinedRepo:
    """Adapter that wraps CharacterRepository + AssetRepository for create_app().

    The Review UI expects a single object with methods from both repos.
    GET routes call methods synchronously (no await), POST routes use async.
    We bridge by storing raw connections for sync reads and delegating
    writes to the async repo methods.
    """

    def __init__(self, char_repo: SQLiteCharacterRepository, asset_repo: SQLiteAssetRepository):
        self._char = char_repo
        self._asset = asset_repo

    # -- Character methods (sync — called from GET routes) --
    def list_characters(self) -> list:
        """Sync version: read characters directly from SQLite."""
        conn = self._char._get_conn()
        rows = conn.execute(
            "SELECT * FROM characters ORDER BY created_at"
        ).fetchall()
        return [self._char._row_to_character(r) for r in rows]

    def get_character(self, character_id: str):
        """Sync version: read character directly from SQLite."""
        conn = self._char._get_conn()
        row = conn.execute(
            "SELECT * FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
        if row is None:
            return None
        return self._char._row_to_character(row)

    # -- Asset methods (sync — called from GET routes) --
    def find_assets(self, character_id: str, asset_type: Optional[str] = None):
        """Sync version: read assets directly from SQLite."""
        conn = self._asset._get_conn()
        if asset_type:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
                "ORDER BY created_at",
                (character_id, asset_type),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? ORDER BY created_at",
                (character_id,),
            ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    def find_approved(self, character_id: str, asset_type: str):
        """Sync version: find approved assets from SQLite."""
        conn = self._asset._get_conn()
        rows = conn.execute(
            "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
            "AND state IN ('approved', 'production') ORDER BY created_at",
            (character_id, asset_type),
        ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    # -- Asset methods (async — called from POST handlers) --
    async def save(self, record: AssetModel) -> str:
        return await self._asset.save(record)

    async def get(self, asset_id: str) -> Optional[AssetModel]:
        return await self._asset.get(asset_id)

    async def update_state(self, asset_id: str, new_state: str) -> None:
        return await self._asset.update_state(asset_id, new_state)

    async def find_by_character(self, character_id: str, asset_type: Optional[str] = None):
        return await self._asset.find_by_character(character_id, asset_type)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main():
    print("=" * 70)
    print("  Identity Lock — Lily Bunny Multi-Angle Reference Sheets")
    print("=" * 70)
    print()

    # -- Precondition: ComfyUI must be running --
    if not check_comfyui():
        sys.exit(1)

    # -- Initialize pipeline components --
    print("\n[1/5] Initializing pipeline components...")
    backend = ComfyUIBackend(server_url=COMFYUI_URL)
    prompt_builder = PromptBuilder()
    scorer = IdentityScorer()
    asset_repo = SQLiteAssetRepository(db_path=DB_PATH)
    char_repo = SQLiteCharacterRepository(db_path=DB_PATH)
    diversity = DiversityFilter(n_clusters=5)
    combined_repo = _CombinedRepo(char_repo, asset_repo)
    print("  ✓ ComfyUIBackend, PromptBuilder, IdentityScorer, repos, DiversityFilter ready")

    # -- Ensure Lily Bunny character exists in the repository --
    print("\n[2/5] Ensuring Lily Bunny character record...")
    existing = await char_repo.find_character_by_name(CHARACTER_NAME)
    if existing:
        character_id = existing.id
        print(f"  ✓ Character '{CHARACTER_NAME}' found (id={character_id})")
    else:
        char = CharacterModel(
            name=CHARACTER_NAME,
            category="main",
            species="rabbit",
            bio_data={
                "appearance": "white fur, pink ears, big blue eyes",
                "default_outfit": "pink dress with white lace, blue bow",
                "style": "Pixar-quality, Cocomelon-inspired, bright colorful nursery world",
            },
        )
        character_id = await char_repo.save_character(char)
        print(f"  ✓ Character '{CHARACTER_NAME}' created (id={character_id})")

    # Build CharacterPrompt for prompt generation
    character = CharacterPrompt(
        name=CHARACTER_NAME,
        species="rabbit",
        appearance="white fur, pink ears, big blue eyes",
        outfit="pink dress with white lace, blue bow",
        style="Pixar-quality, Cocomelon-inspired, bright colorful nursery world",
    )

    # Create output directory
    UNIVERSE_DIR.mkdir(parents=True, exist_ok=True)

    # -- Batch ID for lineage tracking --
    batch_id = f"identity_lock_{int(time.time())}"

    # -- Generate reference sheets for each angle --
    print(f"\n[3/5] Generating reference sheet candidates...")
    print(f"  Batch ID: {batch_id}")

    total_generated = 0
    total_shortlisted = 0
    results: dict[str, dict] = {}

    for angle_config in ANGLES:
        angle_name = angle_config["name"]
        angle = angle_config["angle"]
        count = angle_config["count"]
        shortlist_size = angle_config["shortlist_size"]

        print(f"\n  {'─' * 54}")
        print(f"  Angle: {angle_name} ({angle}) — {count} candidates, shortlist top {shortlist_size}")
        print(f"  {'─' * 54}")

        # Build prompt for this angle
        positive, negative = prompt_builder.build(
            character=character,
            asset_type="reference",
            variant=angle_name,
            angle=angle,
        )
        print(f"  Prompt: {positive[:120]}...")

        # Generate seeds
        seeds = _generate_seeds(count)

        generated_images: list[Image.Image] = []
        generated_seeds: list[int] = []
        generation_errors = 0

        for i, seed in enumerate(seeds):
            gen_input = GenerationInput(
                prompt=positive,
                negative_prompt=negative,
                seed=seed,
                width=1024,
                height=1024,
                num_images=1,
            )
            try:
                output = backend.generate(gen_input, asset_type="reference_sheet")
                if output.images:
                    generated_images.append(output.images[0])
                    generated_seeds.append(seed)
                else:
                    generation_errors += 1
                    if generation_errors <= 3:
                        err_msg = output.metadata.get("error", "unknown error")
                        print(f"  ⚠ Image {i+1}/{count}: empty result ({err_msg})")
            except Exception as exc:
                generation_errors += 1
                if generation_errors <= 3:
                    print(f"  ⚠ Image {i+1}/{count}: {exc}")

            if (i + 1) % 10 == 0 or i == count - 1:
                print(f"  Progress: {i+1}/{count} attempted, {len(generated_images)} successful"
                      f"{' ⚠' if generation_errors > 0 else ''}")

        if not generated_images:
            print(f"  ✗ No images generated for '{angle_name}' — skipping angle")
            results[angle_name] = {"generated": 0, "scored": 0, "shortlisted": 0, "error": "no images"}
            continue

        print(f"  ✓ {len(generated_images)}/{count} images generated successfully")

        # -- Score all generated images --
        scored_assets: list[tuple[Image.Image, float, AssetModel]] = []
        for idx, img in enumerate(generated_images):
            scores = scorer.score_all(img)
            brand = scorer.brand_score(img)
            brand_total = brand.get("total", 0.0)

            asset = AssetModel(
                character_id=character_id,
                asset_type="reference",
                variant=angle_name,
                state="scored",
                file_path="",
                prompt=positive,
                seed=generated_seeds[idx],
                model_id="ComfyUI+Flux",
                scores=scores,
                brand_score=brand_total,
                lineage={
                    "generation_batch": batch_id,
                    "candidate_pool": count,
                    "version_history": [],
                    "asset_type": "reference",
                },
            )
            try:
                asset_id = await asset_repo.save(asset)
                asset.id = asset_id
            except Exception as exc:
                logger.warning("Failed to save scored asset: %s", exc)
                # Use a running ID for diversity filtering
                asset.id = f"temp_{angle_name}_{idx}"

            scored_assets.append((img, brand_total, asset))

        scored_count = len(scored_assets)
        print(f"  ✓ {scored_count} images scored (BrandScore range: "
              f"{min(s[1] for s in scored_assets):.3f} – {max(s[1] for s in scored_assets):.3f})")

        # -- Run diversity filter --
        images_for_filter = [item[0] for item in scored_assets]
        scores_for_filter = [item[1] for item in scored_assets]

        selected = diversity.cluster_and_select(
            images=images_for_filter,
            scores=scores_for_filter,
            n_select=shortlist_size,
        )
        print(f"  ✓ Diversity filter selected {len(selected)}/{shortlist_size} candidates from "
              f"{len(scored_assets)} scored")

        # -- Shortlist selected assets --
        angle_shortlisted = 0
        for idx_in_selected, score in selected:
            _img, _brand_total, asset = scored_assets[idx_in_selected]
            if asset.id and not asset.id.startswith("temp_"):
                try:
                    await asset_repo.update_state(asset.id, "shortlisted")
                    angle_shortlisted += 1
                except Exception as exc:
                    logger.warning("Failed to shortlist asset '%s': %s", asset.id, exc)
            else:
                angle_shortlisted += 1

        print(f"  ✓ {angle_shortlisted} assets shortlisted for human review")
        total_generated += len(generated_images)
        total_shortlisted += angle_shortlisted

        results[angle_name] = {
            "generated": len(generated_images),
            "scored": scored_count,
            "shortlisted": angle_shortlisted,
        }

    # -- Summary --
    print(f"\n{'=' * 70}")
    print(f"  GENERATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Batch ID:      {batch_id}")
    print(f"  Character:     {CHARACTER_NAME} ({character_id})")
    print(f"  DB:            {DB_PATH}")
    print(f"  Universe dir:  {UNIVERSE_DIR}")
    print(f"  Total generated:  {total_generated}")
    print(f"  Total shortlisted: {total_shortlisted}")
    print()
    for angle_name, r in results.items():
        err = f" — ERROR: {r.get('error', '')}" if r.get("error") else ""
        print(f"  {angle_name:10s}: {r['generated']:3d} generated, {r['scored']:3d} scored, "
              f"{r['shortlisted']:2d} shortlisted{err}")
    print()

    # -- Start Review UI for human review --
    print(f"{'=' * 70}")
    print(f"  [4/5] Starting Review UI for human review...")
    print(f"{'=' * 70}")
    print()
    print(f"  The Review UI is starting at http://localhost:8000")
    print()
    print(f"  To review reference sheet candidates:")
    print(f"    1. Open http://localhost:8000 in your browser")
    print(f"    2. If the dashboard shows no data, navigate directly to:")
    print(f"       http://localhost:8000/review/{character_id}?asset_type=reference&batch=true&grid=4x4")
    print(f"    3. For each angle (front, 3/4, profile, back):")
    print(f"       - Review shortlisted candidates")
    print(f"       - Compare side-by-side with reference images")
    print(f"       - Click 'Approve & Promote' to lock a winner")
    print(f"    4. Approved assets will transition: shortlisted → approved → production")
    print()
    print(f"  ⚠ D-15 Approval thresholds for reference sheets: ≥95% identity similarity recommended")
    print(f"  ⚠ This approval is ONE-WAY (D-05) — changing references later requires")
    print(f"    re-scoring all downstream assets (expressions, poses, outfits).")
    print()
    print(f"  [5/5] Starting Review UI server...")
    print()

    import uvicorn
    from src.review_ui.app import create_app

    app = create_app(asset_repo=combined_repo)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(main())

#!/usr/bin/env python3
"""generate_wardrobe.py — Wardrobe Expansion: Outfit generation for Lily Bunny.

Executes stage 4 of the Progressive Locking Pipeline (D-05/D-06):
Wardrobe Expansion produces a complete outfit library (12+ variants) that
completes the character asset production for Phase 1b.

Pipeline: ComfyUIBackend(Flux) → PromptBuilder → IdentityScorer →
          DiversityFilter → SQLiteAssetRepository → human review → Universe Library

Requires:
    - Identity Lock (reference sheets) completed first
    - Body Lock (poses) completed (outfits use pose body proportions)
    - ComfyUI running at http://localhost:8188 with Flux model installed
    - Approved front reference sheet in the asset repository

Usage:
    python scripts/generate_wardrobe.py
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

# Number of candidates per outfit variant
CANDIDATES_PER_OUTFIT = 60
SHORTLIST_SIZE = 12

# Output directory for approved outfit images
UNIVERSE_DIR = Path("Universe/Characters/Lily Bunny/outfits")

COMFYUI_URL = "http://localhost:8188"
DB_PATH = "catalog.db"

# Full-body dimensions for outfits (portrait ratio ~9:16)
OUTFIT_WIDTH = 768
OUTFIT_HEIGHT = 1344

# Outfit variants to generate (based on Lily Bunny bio.md and PHASE1.md clothing library)
OUTFITS: list[dict[str, str]] = [
    {"name": "default", "description": "pink dress with white lace, blue bow"},
    {"name": "winter", "description": "winter coat with scarf, mittens, boots"},
    {"name": "rain", "description": "yellow rain jacket, rain boots, umbrella"},
    {"name": "pajamas", "description": "pajamas with bunny print, slippers"},
    {"name": "swimsuit", "description": "swimsuit, floaties, beach hat"},
    {"name": "princess", "description": "princess costume, tiara, sparkly dress"},
    {"name": "doctor", "description": "doctor costume, stethoscope, white coat"},
    {"name": "firefighter", "description": "firefighter helmet, yellow coat, boots"},
    {"name": "astronaut", "description": "astronaut suit, helmet, space backpack"},
    {"name": "farmer", "description": "farmer outfit, overalls, straw hat"},
    {"name": "chef", "description": "chef outfit, apron, chef hat"},
    {"name": "teacher", "description": "teacher outfit, glasses, cardigan"},
    {"name": "police", "description": "police officer uniform, hat, badge"},
    {"name": "construction", "description": "construction vest, hard hat, tools"},
    {"name": "halloween", "description": "witch costume, hat, broom"},
    {"name": "christmas", "description": "christmas dress, santa hat, ornaments"},
    {"name": "sports", "description": "sports uniform, jersey, sneakers"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def check_comfyui() -> bool:
    """Verify ComfyUI is reachable at the configured URL."""
    import requests

    try:
        r = requests.get(f"{COMFYUI_URL}/", timeout=5)
        r.raise_for_status()
        print(f"  ✓ ComfyUI reachable at {COMFYUI_URL}")
        return True
    except Exception as exc:
        print(f"  ✗ ComfyUI not reachable at {COMFYUI_URL}: {exc}")
        print("    Start ComfyUI first, then re-run this script.")
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
    """Adapter that wraps CharacterRepository + AssetRepository for create_app()."""

    def __init__(self, char_repo: SQLiteCharacterRepository, asset_repo: SQLiteAssetRepository):
        self._char = char_repo
        self._asset = asset_repo

    def list_characters(self) -> list:
        conn = self._char._get_conn()
        rows = conn.execute("SELECT * FROM characters ORDER BY created_at").fetchall()
        return [self._char._row_to_character(r) for r in rows]

    def get_character(self, character_id: str):
        conn = self._char._get_conn()
        row = conn.execute("SELECT * FROM characters WHERE id = ?", (character_id,)).fetchone()
        if row is None:
            return None
        return self._char._row_to_character(row)

    def find_assets(self, character_id: str, asset_type: Optional[str] = None):
        conn = self._asset._get_conn()
        if asset_type:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? ORDER BY created_at",
                (character_id, asset_type),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? ORDER BY created_at",
                (character_id,),
            ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    def find_approved(self, character_id: str, asset_type: str):
        conn = self._asset._get_conn()
        rows = conn.execute(
            "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
            "AND state IN ('approved', 'production') ORDER BY created_at",
            (character_id, asset_type),
        ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

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
    print("  Wardrobe Expansion — Lily Bunny Outfit Library (17 variants)")
    print("=" * 70)
    print()

    batch_id = f"wardrobe_{int(time.time())}"

    # -- Precondition: ComfyUI must be running --
    if not check_comfyui():
        print(f"\n  Batch ID: {batch_id}")
        print("  Generated 0 outfits (ComfyUI not running)")
        print("  The script is ready. Start ComfyUI and re-run.")
        print()

    # -- Initialize pipeline components --
    print("\n[1/6] Initializing pipeline components...")
    backend = ComfyUIBackend(server_url=COMFYUI_URL)
    prompt_builder = PromptBuilder()
    scorer = IdentityScorer()
    asset_repo = SQLiteAssetRepository(db_path=DB_PATH)
    char_repo = SQLiteCharacterRepository(db_path=DB_PATH)
    diversity = DiversityFilter(n_clusters=5)
    combined_repo = _CombinedRepo(char_repo, asset_repo)
    print("  ✓ ComfyUIBackend, PromptBuilder, IdentityScorer, repos, DiversityFilter ready")

    # -- Ensure Lily Bunny character exists --
    print("\n[2/6] Ensuring Lily Bunny character record...")
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
                "default_outfit": OUTFITS[0]["description"],
                "style": "Pixar-quality, Cocomelon-inspired, bright colorful nursery world",
            },
        )
        character_id = await char_repo.save_character(char)
        print(f"  ✓ Character '{CHARACTER_NAME}' created (id={character_id})")

    character = CharacterPrompt(
        name=CHARACTER_NAME,
        species="rabbit",
        appearance="white fur, pink ears, big blue eyes",
        outfit="pink dress with white lace, blue bow",
        style="Pixar-quality, Cocomelon-inspired, bright colorful nursery world",
    )

    # Create output directory
    UNIVERSE_DIR.mkdir(parents=True, exist_ok=True)

    # -- Find approved front reference sheet for identity scoring --
    print("\n[3/6] Loading approved front reference sheet...")
    front_ref_id: Optional[str] = None
    reference_image_path: Optional[str] = None
    try:
        approved_refs = combined_repo.find_approved(character_id, "reference")
        front_refs = [a for a in approved_refs if a.variant == "front"]
        if front_refs:
            front_ref_id = front_refs[0].id
            reference_image_path = front_refs[0].file_path
            print(f"  ✓ Front reference sheet found (id={front_ref_id}, path={reference_image_path})")
        else:
            print("  ⚠ No approved front reference found. Outfits will be generated")
            print("    without identity scoring reference.")
    except Exception as exc:
        print(f"  ⚠ Could not load reference sheet: {exc}")

    # -- Generate outfits sequentially --
    print(f"\n[4/6] Generating outfit candidates...")
    print(f"  Batch ID: {batch_id}")
    print(f"  Candidates per outfit: {CANDIDATES_PER_OUTFIT}")
    print(f"  Shortlist size per outfit: {SHORTLIST_SIZE}")
    print(f"  Dimensions: {OUTFIT_WIDTH}x{OUTFIT_HEIGHT} (full-body)")
    print(f"  Estimated total: {len(OUTFITS) * CANDIDATES_PER_OUTFIT} images")
    print()

    total_generated = 0
    total_shortlisted = 0
    results: dict[str, dict] = {}

    for idx, outfit_config in enumerate(OUTFITS):
        outfit_name = outfit_config["name"]
        outfit_desc = outfit_config["description"]
        count = CANDIDATES_PER_OUTFIT
        shortlist_size = SHORTLIST_SIZE

        print(f"  {'─' * 54}")
        print(f"  Outfit {idx + 1}/{len(OUTFITS)}: '{outfit_name}' — {outfit_desc}")
        print(f"    {count} candidates, shortlist top {shortlist_size}")
        print(f"  {'─' * 54}")

        # Build prompt with the outfit-specific description
        character_with_outfit = CharacterPrompt(
            name=character.name,
            species=character.species,
            appearance=character.appearance,
            outfit=outfit_desc,
            style=character.style,
        )

        positive, negative = prompt_builder.build(
            character=character_with_outfit,
            asset_type="outfit",
            variant=outfit_name,
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
                width=OUTFIT_WIDTH,
                height=OUTFIT_HEIGHT,
                num_images=1,
            )
            try:
                output = backend.generate(gen_input, asset_type="outfit")
                if output.images:
                    generated_images.append(output.images[0])
                    generated_seeds.append(seed)
                else:
                    generation_errors += 1
                    if generation_errors <= 3:
                        err_msg = output.metadata.get("error", "unknown error")
                        print(f"    ⚠ Image {i+1}/{count}: empty result ({err_msg})")
            except Exception as exc:
                generation_errors += 1
                if generation_errors <= 3:
                    print(f"    ⚠ Image {i+1}/{count}: {exc}")

            if (i + 1) % 10 == 0 or i == count - 1:
                print(f"    Progress: {i+1}/{count} attempted, {len(generated_images)} successful"
                      f"{' ⚠' if generation_errors > 0 else ''}")

        if not generated_images:
            print(f"  ✗ No images generated for '{outfit_name}' — skipping")
            results[outfit_name] = {"generated": 0, "scored": 0, "shortlisted": 0, "error": "no images"}
            continue

        print(f"  ✓ {len(generated_images)}/{count} images generated successfully")

        # -- Score all generated images --
        scored_assets: list[tuple[Image.Image, float, AssetModel]] = []
        for img_idx, img in enumerate(generated_images):
            scores = scorer.score_all(img)
            brand = scorer.brand_score(img)
            brand_total = brand.get("total", 0.0)

            asset = AssetModel(
                character_id=character_id,
                asset_type="outfit",
                variant=outfit_name,
                state="scored",
                file_path="",
                prompt=positive,
                seed=generated_seeds[img_idx],
                model_id="ComfyUI+Flux",
                scores=scores,
                brand_score=brand_total,
                lineage={
                    "generation_batch": batch_id,
                    "candidate_pool": count,
                    "version_history": [],
                    "reference_asset_id": front_ref_id,
                    "asset_type": "outfit",
                },
            )
            try:
                asset_id = await asset_repo.save(asset)
                asset.id = asset_id
            except Exception as exc:
                logger.warning("Failed to save scored asset: %s", exc)
                asset.id = f"temp_{outfit_name}_{img_idx}"

            scored_assets.append((img, brand_total, asset))

        scored_count = len(scored_assets)
        if scored_count > 0:
            print(f"  ✓ {scored_count} images scored (BrandScore range: "
                  f"{min(s[1] for s in scored_assets):.3f} – {max(s[1] for s in scored_assets):.3f})")
        else:
            print(f"  ✗ No images survived scoring for '{outfit_name}'")
            results[outfit_name] = {"generated": len(generated_images), "scored": 0, "shortlisted": 0, "error": "no scored"}
            continue

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
        outfit_shortlisted = 0
        for sel_idx, score in selected:
            _img, _brand_total, asset = scored_assets[sel_idx]
            if asset.id and not asset.id.startswith("temp_"):
                try:
                    await asset_repo.update_state(asset.id, "shortlisted")
                    outfit_shortlisted += 1
                except Exception as exc:
                    logger.warning("Failed to shortlist asset '%s': %s", asset.id, exc)
            else:
                outfit_shortlisted += 1

        print(f"  ✓ {outfit_shortlisted} assets shortlisted for human review")
        total_generated += len(generated_images)
        total_shortlisted += outfit_shortlisted

        results[outfit_name] = {
            "generated": len(generated_images),
            "scored": scored_count,
            "shortlisted": outfit_shortlisted,
        }

    # -- Summary --
    print(f"\n{'=' * 70}")
    print(f"  GENERATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Batch ID:      {batch_id}")
    print(f"  Character:     {CHARACTER_NAME} ({character_id})")
    print(f"  DB:            {DB_PATH}")
    print(f"  Universe dir:  {UNIVERSE_DIR}")
    print(f"  Reference:     {reference_image_path or '(none)'}")
    print(f"  Total generated:  {total_generated}")
    print(f"  Total shortlisted: {total_shortlisted}")
    print()

    success_count = sum(1 for r in results.values() if r.get("error") is None)
    error_count = len(results) - success_count
    print(f"  Outfits with candidates: {success_count}/{len(OUTFITS)}")
    if error_count:
        print(f"  Outfits with errors: {error_count}")
        for name, r in results.items():
            if r.get("error"):
                print(f"    ✗ {name}: {r['error']}")
    print()

    for outfit_name, r in sorted(results.items()):
        err = f" — ERROR: {r.get('error', '')}" if r.get("error") else ""
        print(f"  {outfit_name:15s}: {r['generated']:3d} generated, {r['scored']:3d} scored, "
              f"{r['shortlisted']:2d} shortlisted{err}")

    # -- Start Review UI for human review --
    print()
    print(f"{'=' * 70}")
    print(f"  [5/6] Starting Review UI for human review...")
    print(f"{'=' * 70}")
    print()
    print(f"  The Review UI is starting at http://localhost:8000")
    print()
    print(f"  To review outfit candidates:")
    print(f"    1. Open http://localhost:8000 in your browser")
    print(f"    2. Navigate to:")
    print(f"       http://localhost:8000/review/{character_id}?asset_type=outfit&batch=true&grid=4x4")
    print(f"    3. For each of the {len(OUTFITS)} outfits:")
    print(f"       - Review shortlisted candidates")
    print(f"       - Compare against the front reference sheet (left panel)")
    print(f"       - Key check: Is Lily still recognizable despite the outfit change?")
    print(f"       - Click 'Approve & Promote' to lock a winner")
    print(f"    4. Approved assets will transition: shortlisted → approved → production")
    print()
    print(f"  ⚠ D-14 Approval thresholds for outfits: 80–92% identity similarity")
    print(f"  ⚠ D-15 Approval zones: ≥95% auto-pass, 80–95% normal review, 70–80% diversity only, <70% reject")
    print(f"  ⚠ Outfits have the most lenient thresholds because clothing changes alter silhouette")
    print()
    print(f"  Starting Review UI server...")
    print()

    import uvicorn
    from src.review_ui.app import create_app

    app = create_app(asset_repo=combined_repo)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(main())

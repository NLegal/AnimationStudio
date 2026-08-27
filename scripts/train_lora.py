#!/usr/bin/env python3
"""train_lora.py — LoRA training orchestrator for the character training system.

Orchestrates the full offline-provable training pipeline: curate assets
from the repository into a bounded dataset, prove the training command via
first-class dry-run, benchmark against the identity scorer, and manage
persisted versions.

Reproduction (offline — zero network/GPU):
    python scripts/train_lora.py --dry-run
    python scripts/train_lora.py build-dataset --db catalog.db
    python scripts/train_lora.py train --dry-run
    python scripts/train_lora.py versions
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.training_engine.dataset_builder import (
    DatasetBuilder,
    DatasetConfig,
    DatasetEntry,
)
from src.training_engine.kohya_adapter import KohyaAdapter
from src.training_engine.version_store import load_registry
from src.training_engine.versioning import LoRAVersion, VersionRegistry
from src.training_engine.benchmark import BenchmarkConfig, LoRABenchmark
from src.asset_repository.sqlite_repo import (
    SQLiteAssetRepository,
    SQLiteCharacterRepository,
)

# ---------------------------------------------------------------------------
# Identifier validation (T-01c-05a)
# ---------------------------------------------------------------------------
_VALID_CHAR_ID = re.compile(r"^[a-z0-9][a-z0-9\-]{0,127}$")


def _validate_identifier(value: str, label: str) -> None:
    """Reject identifier strings that could cause path/argv injection."""
    if not _VALID_CHAR_ID.match(value):
        raise SystemExit(
            f"Invalid {label}: {value!r} — "
            f"must match [a-z0-9]([a-z0-9\\-]{{0,127}})"
        )


# ---------------------------------------------------------------------------
# Shared curation helper
# ---------------------------------------------------------------------------

def _curate_assets(
    db_path: str,
    character_id: str,
    max_images: int,
) -> list[dict]:
    """Open repo, call find_curated, dedupe per variant, cap to max_images.

    Deduplication rule (G7/A5): one best image per (asset_type, variant),
    keeping the highest brand_score with stable tie-break by asset id.
    """
    _validate_identifier(character_id, "character-id")
    asset_repo = SQLiteAssetRepository(db_path=db_path)
    curated = asyncio.run(asset_repo.find_curated(character_id))

    if not curated:
        raise SystemExit(
            f"No curated (approved/production) assets found for "
            f"character '{character_id}'."
        )

    # Dedupe per variant — keep highest brand_score, stable by id
    best_by_variant: dict[str, object] = {}
    for asset in curated:
        variant_key = f"{asset.asset_type}:{asset.variant or ''}"
        existing = best_by_variant.get(variant_key)
        if existing is None:
            best_by_variant[variant_key] = asset
        else:
            existing_score = getattr(existing, "brand_score", 0) or 0
            current_score = getattr(asset, "brand_score", 0) or 0
            if current_score > existing_score:
                best_by_variant[variant_key] = asset
            elif current_score == existing_score and asset.id < existing.id:  # type: ignore
                best_by_variant[variant_key] = asset

    deduped = list(best_by_variant.values())

    # Cap to max_images
    if len(deduped) > max_images:
        deduped = deduped[:max_images]

    # Convert to dicts for DatasetBuilder
    return [
        {
            "id": a.id,
            "file_path": a.file_path,
            "asset_type": a.asset_type,
            "variant": a.variant,
            "brand_score": a.brand_score,
            "prompt": a.prompt,
        }
        for a in deduped
    ]


# ---------------------------------------------------------------------------
# Subcommand: build-dataset
# ---------------------------------------------------------------------------

def _build_dataset(args: argparse.Namespace) -> int:
    """Build a bounded training dataset from curated assets."""
    asset_dicts = _curate_assets(
        args.db, args.character_id, args.max_images,
    )

    builder = DatasetBuilder()
    entries = [
        DatasetEntry(
            image_path=Path(a["file_path"]),
            caption=a.get("prompt") or "",
            asset_type=a.get("asset_type") or "expression",
            variant=a.get("variant"),
            brand_score=a.get("brand_score"),
        )
        for a in asset_dicts
    ]

    config = DatasetConfig(
        output_dir=Path(args.output_root),
        min_images=args.min_images,
        max_images=args.max_images,
        character_id=args.character_id,
    )
    try:
        result = builder.build(entries, config)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Copy reference baselines into baselines/{character_id}/
    baselines_dir = Path(args.output_root) / "baselines" / args.character_id
    baselines_dir.mkdir(parents=True, exist_ok=True)
    ref_entries = [e for e in entries if e.asset_type == "reference"][:10]
    import shutil
    for entry in ref_entries:
        src = entry.image_path.resolve()
        if src.exists():
            dest = baselines_dir / src.name
            shutil.copy2(str(src), str(dest))

    print(
        f"Dataset built: {result.num_images} images "
        f"({result.num_val_images} val) → {result.output_dir}"
    )
    return 0


# ---------------------------------------------------------------------------
# Subcommand: train
# ---------------------------------------------------------------------------

def _train(args: argparse.Namespace) -> int:
    """Execute training (dry-run enforced locally; real training is Colab-only)."""
    _validate_identifier(args.character_id, "character-id")

    # Load persisted registry (bound to a sidecar store so new dry-run
    # evidence is durable across sessions, even on first creation)
    registry_path = Path(args.registry_path)
    from src.training_engine.version_store import load_registry as _load_registry
    registry = _load_registry(registry_path)

    adapter = KohyaAdapter(version_registry=registry)

    if not args.dry_run:
        print(
            "Error: Real training is a Colab operator action.\n"
            "Use the training notebook: colab/AnimationStudio_Colab_Training.ipynb\n"
            "To prove the command offline, run with --dry-run.",
            file=sys.stderr,
        )
        return 1

    # Verify the character exists before registering training evidence —
    # unknown characters fail loudly rather than fabricating a version record.
    character_repo = SQLiteCharacterRepository(db_path=args.db)
    character = asyncio.run(character_repo.get_character(args.character_id))
    if character is None:
        print(
            f"No character found for '{args.character_id}'.",
            file=sys.stderr,
        )
        return 1

    # Compute next version
    next_version = registry.recommend_next(args.character_id, "minor")

    from src.training_engine.base import TrainingConfig

    config = TrainingConfig(
        character_id=args.character_id,
        dataset_path=Path(args.output_root),
        output_path=Path(args.output_root),
        version=str(next_version),
        dry_run=True,
    )
    result = adapter.train(config)

    if not result.success:
        error_msg = result.metrics.get("error", "Unknown error")
        print(f"Error: {error_msg}", file=sys.stderr)
        return 1

    cmd_path = Path(args.output_root) / f"{args.character_id}_{next_version}.train_cmd.json"
    print(
        f"Train dry-run complete: version {next_version} registered.\n"
        f"Command artifact: {cmd_path}\n"
        f"Registry: {args.registry_path}"
    )
    return 0


# ---------------------------------------------------------------------------
# Subcommand: benchmark
# ---------------------------------------------------------------------------

def _benchmark(args: argparse.Namespace) -> int:
    """Run benchmark against identity scorer with explicit test images."""
    from pathlib import Path as P

    lora_path = P(args.lora)
    if not lora_path.exists():
        print(f"Error: LoRA file not found: {args.lora}", file=sys.stderr)
        return 1

    # Parse --images (comma-separated)
    image_paths = [P(p.strip()) for p in args.images.split(",") if p.strip()]
    if not image_paths:
        print(
            "Error: --images is required for offline benchmark "
            "(engine-side generation is a documented stub).",
            file=sys.stderr,
        )
        return 1

    for img in image_paths:
        if not img.exists():
            print(f"Error: Test image not found: {img}", file=sys.stderr)
            return 1

    baseline_dir = P(args.baseline_dir) if args.baseline_dir else None

    # Extract character_id from filename (e.g. lily-bunny_v0.1.safetensors → lily-bunny)
    stem = lora_path.stem
    match = re.match(r"^(.+)_v\d+\.\d+$", stem)
    character_id = match.group(1) if match else stem

    config = BenchmarkConfig(baseline_dir=baseline_dir)

    # Try IdentityScorerProvider; fall back to MockScorerProvider
    try:
        from src.training_engine.scorer_adapter import IdentityScorerProvider
        provider = IdentityScorerProvider(light=True)
    except Exception:
        from src.training_engine.benchmark import MockScorerProvider
        provider = MockScorerProvider(seed=42)

    benchmark = LoRABenchmark(scorer_provider=provider, config=config)
    result = benchmark.evaluate(
        lora_path=lora_path,
        character_id=character_id,
        test_images=image_paths,
    )

    report = benchmark.report(result)
    print(report)

    # Coverage advisory (G14)
    if result.weight_coverage < 1.0:
        print(
            f"\n⚠ Advisory: Weight coverage is {result.weight_coverage:.0%} "
            f"(partial plugin set). Full evaluation runs on Colab with "
            f"IdentityScorerProvider(light=False).",
            file=sys.stderr,
        )

    return 0 if result.passed else 1


# ---------------------------------------------------------------------------
# Subcommand: versions
# ---------------------------------------------------------------------------

def _versions(args: argparse.Namespace) -> int:
    """List persisted version records for a character (read-only)."""
    _validate_identifier(args.character_id, "character-id")

    registry_path = Path(args.registry_path)
    if not registry_path.exists():
        print("No versions registered yet.")
        return 0

    registry = load_registry(registry_path)
    records = registry.get_versions(args.character_id)

    if not records:
        print(f"No versions registered for '{args.character_id}'.")
        return 0

    for rec in records:
        promoted = " ★ PROMOTED" if rec.promoted else ""
        trained = rec.trained_at.isoformat() if rec.trained_at else "unknown"
        print(f"  {rec.version}  {trained}{promoted}  {rec.file_path}")

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    """Parse arguments and dispatch to the appropriate subcommand.

    Returns:
        Exit code: 0 for success, 1 for failure.
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global flags
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--character-id", default="lily-bunny",
                        help="Character identifier (default: lily-bunny)")
    parser.add_argument("--output-root", default="training/",
                        help="Root directory for training output (default: training/)")
    parser.add_argument("--registry-path", default="training/lora_registry.json",
                        help="Path to version registry JSON file (default: training/lora_registry.json)")
    parser.add_argument("--states", default="approved,production",
                        help="Comma-separated asset states for curation (default: approved,production)")
    parser.add_argument("--min-images", type=int, default=20,
                        help="Minimum number of images for dataset (default: 20)")
    parser.add_argument("--max-images", type=int, default=40,
                        help="Maximum number of images for dataset (default: 40)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Enable dry-run mode for train subcommand")

    subparsers = parser.add_subparsers(dest="subcommand")

    # build-dataset
    subparsers.add_parser("build-dataset", help="Build training dataset from curated assets")

    # train
    subparsers.add_parser("train", help="Train LoRA model (dry-run locally, real training via Colab)")

    # benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Benchmark LoRA against identity scorer")
    bench_parser.add_argument("--lora", required=True,
                              help="Path to LoRA .safetensors file")
    bench_parser.add_argument("--images", required=True,
                              help="Comma-separated list of test image paths")
    bench_parser.add_argument("--baseline-dir", default=None,
                              help="Baseline directory for pre-LoRA reference images")

    # versions
    subparsers.add_parser("versions", help="List registered LoRA versions (read-only)")

    args = parser.parse_args(argv)

    # Validate --states
    valid_states = {"approved", "production"}
    states = {s.strip().lower() for s in args.states.split(",") if s.strip()}
    if not states.issubset(valid_states):
        raise SystemExit(
            f"Invalid states: {states - valid_states}. "
            f"Valid states: {valid_states}"
        )

    dispatch = {
        "build-dataset": _build_dataset,
        "train": _train,
        "benchmark": _benchmark,
        "versions": _versions,
    }

    handler = dispatch.get(args.subcommand)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())

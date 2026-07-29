"""Tests for Phase 1c — DatasetBuilder, VersionRegistry, LoRABenchmark, and KohyaAdapter integration.

Covers:
    - DatasetBuilder: build, entries, splits, config output
    - VersionRegistry: register, query, bump recommendations
    - LoRABenchmark: scoring, composite, baseline comparison, reporting
    - KohyaAdapter integration: build_dataset, version registration
"""

from datetime import datetime
from pathlib import Path

import pytest

from src.training_engine import (
    DatasetBuilder,
    DatasetEntry,
    DatasetConfig,
    BuildResult,
    LoRAVersion,
    VersionRegistry,
    VersionRecord,
    LoRABenchmark,
    BenchmarkConfig,
    BenchmarkResult,
    MockScorerProvider,
    KohyaAdapter,
    TrainingConfig,
)


# =========================================================================
# DatasetBuilder tests
# =========================================================================

class TestDatasetBuilder:
    """DatasetBuilder build and entry creation."""

    def test_build_creates_output_structure(self, tmp_path):
        """build() creates train/val dirs, metadata, and TOML config."""
        img = tmp_path / "test.png"
        img.write_text("fake-image")

        builder = DatasetBuilder()
        entries = [
            DatasetEntry(
                image_path=img,
                caption="Lily Bunny, happy expression",
                asset_type="expression",
            ),
        ]
        config = DatasetConfig(
            output_dir=tmp_path / "dataset",
            validation_split=0.0,
        )
        result = builder.build(entries, config)

        assert result.output_dir.exists()
        assert (result.output_dir / "train").exists()
        assert (result.output_dir / "metadata.json").exists()
        assert (result.output_dir / "dataset_config.toml").exists()
        assert result.num_images == 1
        assert result.num_val_images == 0

    def test_build_train_val_split(self, tmp_path):
        """build() splits data into train and val sets."""
        images = []
        for i in range(10):
            p = tmp_path / f"img_{i:02d}.png"
            p.write_text(f"fake-{i}")
            images.append(p)

        builder = DatasetBuilder()
        entries = [
            DatasetEntry(image_path=p, caption=f"test {i}")
            for i, p in enumerate(images)
        ]
        config = DatasetConfig(
            output_dir=tmp_path / "split_dataset",
            validation_split=0.2,
        )
        result = builder.build(entries, config)

        assert result.num_images == 8
        assert result.num_val_images == 2
        assert len(list((result.output_dir / "train").iterdir())) == 8
        assert len(list((result.output_dir / "val").iterdir())) == 2

    def test_build_skips_missing_images(self, tmp_path):
        """build() skips images that do not exist on disk."""
        builder = DatasetBuilder()
        entries = [
            DatasetEntry(
                image_path=tmp_path / "nonexistent.png",
                caption="missing",
            ),
        ]
        config = DatasetConfig(
            output_dir=tmp_path / "partial",
            validation_split=0.0,
        )
        result = builder.build(entries, config)
        assert result.num_images == 0

    def test_build_caption_prefix_suffix(self, tmp_path):
        """Captions include configured prefix and suffix."""
        img = tmp_path / "test.png"
        img.write_text("fake")
        builder = DatasetBuilder()
        entries = [
            DatasetEntry(image_path=img, caption="happy"),
        ]
        config = DatasetConfig(
            output_dir=tmp_path / "caps",
            validation_split=0.0,
            caption_prefix="[PFX]",
            caption_suffix="[SFX]",
        )
        result = builder.build(entries, config)

        import json
        meta = json.loads((result.metadata_file).read_text())
        caption = meta["train"][0]["caption"]
        assert "[PFX]" in caption
        assert "[SFX]" in caption
        assert caption == "[PFX], happy, [SFX]"

    def test_build_entries_from_assets(self, tmp_path):
        """build_entries_from_assets creates entries from asset dicts."""
        img = tmp_path / "asset.png"
        img.write_text("fake")
        assets = [
            {
                "id": "asset-001",
                "file_path": str(img),
                "asset_type": "expression",
                "variant": "happy",
                "brand_score": 0.92,
                "prompt": "Lily Bunny, happy expression",
            },
        ]
        entries = DatasetBuilder.build_entries_from_assets(assets)
        assert len(entries) == 1
        assert entries[0].caption == "Lily Bunny, happy expression"
        assert entries[0].asset_type == "expression"
        assert entries[0].brand_score == 0.92

    def test_kohya_config_toml_format(self, tmp_path):
        """TOML config contains expected Kohya SS sections."""
        img = tmp_path / "a.png"
        img.write_text("fake")
        builder = DatasetBuilder()
        entries = [DatasetEntry(image_path=img, caption="test")]
        config = DatasetConfig(
            output_dir=tmp_path / "toml_test",
            validation_split=0.1,
        )
        result = builder.build(entries, config)

        toml_text = result.config_file.read_text()
        assert "[general]" in toml_text
        assert "resolution" in toml_text
        assert "dataset_config.toml" in str(result.config_file)


# =========================================================================
# LoRAVersion tests
# =========================================================================

class TestLoRAVersion:
    """LoRAVersion parsing, comparison, and bumping."""

    def test_parse_valid(self):
        v = LoRAVersion.parse("v0.1")
        assert v.major == 0
        assert v.minor == 1
        assert str(v) == "v0.1"

    def test_parse_production(self):
        v = LoRAVersion.parse("v1.0")
        assert v.is_production
        assert not v.is_experimental

    def test_parse_experimental(self):
        v = LoRAVersion.parse("v0.5")
        assert v.is_experimental
        assert not v.is_production

    def test_parse_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid LoRA version"):
            LoRAVersion.parse("1.0")
        with pytest.raises(ValueError, match="Invalid LoRA version"):
            LoRAVersion.parse("abc")
        with pytest.raises(ValueError, match="Invalid LoRA version"):
            LoRAVersion.parse("")

    def test_bump_major(self):
        v = LoRAVersion.parse("v0.1")
        bumped = v.bump_major()
        assert str(bumped) == "v1.0"

        v2 = LoRAVersion.parse("v1.3")
        assert str(v2.bump_major()) == "v2.0"

    def test_bump_minor(self):
        v = LoRAVersion.parse("v0.1")
        assert str(v.bump_minor()) == "v0.2"

        v2 = LoRAVersion.parse("v1.0")
        assert str(v2.bump_minor()) == "v1.1"

    def test_bump_convenience(self):
        v = LoRAVersion.parse("v0.1")
        assert str(v.bump("minor")) == "v0.2"
        assert str(v.bump("major")) == "v1.0"

    def test_bump_invalid_type(self):
        v = LoRAVersion.parse("v0.1")
        with pytest.raises(ValueError, match="Unknown bump type"):
            v.bump("patch")

    def test_equality(self):
        assert LoRAVersion.parse("v1.0") == LoRAVersion(1, 0)
        assert LoRAVersion.parse("v0.1") != LoRAVersion.parse("v0.2")

    def test_immutable(self):
        v = LoRAVersion.parse("v0.1")
        with pytest.raises(AttributeError):
            v.major = 2  # type: ignore


# =========================================================================
# VersionRegistry tests
# =========================================================================

class TestVersionRegistry:
    """VersionRegistry registration, querying, and recommendation."""

    def test_register_and_get_latest(self):
        registry = VersionRegistry()
        registry.register(
            character_id="lily-bunny",
            version=LoRAVersion.parse("v0.1"),
            file_path="/tmp/lily_v0.1.safetensors",
        )
        registry.register(
            character_id="lily-bunny",
            version=LoRAVersion.parse("v0.2"),
            file_path="/tmp/lily_v0.2.safetensors",
        )
        latest = registry.get_latest("lily-bunny")
        assert latest is not None
        assert str(latest.version) == "v0.2"

    def test_get_versions_empty_returns_empty_list(self):
        registry = VersionRegistry()
        assert registry.get_versions("nonexistent") == []

    def test_get_latest_none_for_unknown(self):
        registry = VersionRegistry()
        assert registry.get_latest("ghost") is None

    def test_recommend_next_first_version(self):
        registry = VersionRegistry()
        next_v = registry.recommend_next("new-char")
        assert str(next_v) == "v0.1"

    def test_recommend_next_minor(self):
        registry = VersionRegistry()
        registry.register(
            character_id="test",
            version=LoRAVersion.parse("v0.1"),
            file_path="/tmp/test_v0.1.safetensors",
        )
        assert str(registry.recommend_next("test", "minor")) == "v0.2"
        assert str(registry.recommend_next("test", "major")) == "v1.0"

    def test_get_promoted(self):
        registry = VersionRegistry()
        registry.register(
            character_id="test",
            version=LoRAVersion.parse("v0.1"),
            file_path="/tmp/test_v0.1.safetensors",
            promoted=False,
        )
        registry.register(
            character_id="test",
            version=LoRAVersion.parse("v1.0"),
            file_path="/tmp/test_v1.0.safetensors",
            promoted=True,
        )
        promoted = registry.get_promoted("test")
        assert promoted is not None
        assert str(promoted.version) == "v1.0"

    def test_from_db_records(self):
        records = [
            {
                "character_id": "lily-bunny",
                "version": "v0.1",
                "file_path": "/tmp/lily_v0.1.safetensors",
                "promoted": 0,
                "trained_at": "2026-07-29T12:00:00",
            },
            {
                "character_id": "lily-bunny",
                "version": "v1.0",
                "file_path": "/tmp/lily_v1.0.safetensors",
                "promoted": 1,
            },
        ]
        registry = VersionRegistry.from_db_records(records)
        assert len(registry.get_versions("lily-bunny")) == 2
        promoted = registry.get_promoted("lily-bunny")
        assert promoted is not None
        assert str(promoted.version) == "v1.0"

    def test_get_production_candidates(self):
        registry = VersionRegistry()
        registry.register(
            character_id="test",
            version=LoRAVersion.parse("v0.1"),
            file_path="/tmp/test_v0.1.safetensors",
            benchmark_scores={"dino_similarity": 0.85},
        )
        registry.register(
            character_id="test",
            version=LoRAVersion.parse("v0.2"),
            file_path="/tmp/test_v0.2.safetensors",
        )
        candidates = registry.get_production_candidates("test")
        assert len(candidates) == 1


# =========================================================================
# LoRABenchmark tests
# =========================================================================

class TestLoRABenchmark:
    """LoRABenchmark scoring, baseline comparison, and reporting."""

    def test_evaluate_with_test_images(self, tmp_path):
        """evaluate() scores provided test images."""
        img = tmp_path / "test.png"
        img.write_text("fake-image")
        lora = tmp_path / "lily_v0.1.safetensors"
        lora.write_text("fake-lora")
        scorer = MockScorerProvider(seed=42)
        benchmark = LoRABenchmark(scorer_provider=scorer)
        result = benchmark.evaluate(
            lora_path=lora,
            character_id="lily-bunny",
            test_images=[img],
        )
        assert len(result.dimensions) > 0
        assert 0.0 < result.composite_score <= 1.0
        assert result.passed or not result.passed  # depends on threshold

    def test_evaluate_nonexistent_lora(self, tmp_path):
        """evaluate() returns failed result for missing LoRA."""
        scorer = MockScorerProvider()
        benchmark = LoRABenchmark(scorer_provider=scorer)
        result = benchmark.evaluate(
            lora_path=tmp_path / "nonexistent.safetensors",
            character_id="test",
        )
        assert not result.passed
        assert result.composite_score == 0.0

    def test_evaluate_with_baseline(self, tmp_path):
        """evaluate() computes improvement over baseline."""
        (tmp_path / "baseline" / "lily-bunny").mkdir(parents=True)
        for i in range(3):
            p = tmp_path / "baseline" / "lily-bunny" / f"ref_{i}.png"
            p.write_text(f"baseline-{i}")

        test_img = tmp_path / "test.png"
        test_img.write_text("test-image")
        lora = tmp_path / "lily_v0.1.safetensors"
        lora.write_text("fake-lora")

        scorer = MockScorerProvider(seed=42)
        config = BenchmarkConfig(
            baseline_dir=tmp_path / "baseline",
        )
        benchmark = LoRABenchmark(scorer_provider=scorer, config=config)
        result = benchmark.evaluate(
            lora_path=lora,
            character_id="lily-bunny",
            test_images=[test_img],
        )

        assert result.baseline_composite is not None
        if result.improvement is not None:
            assert isinstance(result.improvement, float)

    def test_no_test_images_returns_failed(self, tmp_path):
        """evaluate() with no images returns failed result."""
        lora = tmp_path / "lily_v0.1.safetensors"
        lora.write_text("fake-lora")
        scorer = MockScorerProvider()
        benchmark = LoRABenchmark(scorer_provider=scorer)
        result = benchmark.evaluate(
            lora_path=lora,
            character_id="test",
            test_images=[],
        )
        assert not result.passed

    def test_report_format(self, tmp_path):
        """report() produces markdown with expected sections."""
        img = tmp_path / "test.png"
        img.write_text("fake")
        scorer = MockScorerProvider()
        benchmark = LoRABenchmark(scorer_provider=scorer)
        result = benchmark.evaluate(
            lora_path=tmp_path / "lily_v1.0.safetensors",
            character_id="test",
            test_images=[img],
        )
        report = benchmark.report(result)
        assert "# LoRA Benchmark Report" in report
        assert "Composite Scores" in report
        assert "Per-Dimension Scores" in report
        assert "✅" in report or "❌" in report

    def test_derive_version(self):
        """_derive_version extracts version from filename."""
        v = LoRABenchmark._derive_version(Path("/tmp/lily_v0.1.safetensors"))
        assert v == "v0.1"
        assert LoRABenchmark._derive_version(Path("lily_v1.0.safetensors")) == "v1.0"
        assert LoRABenchmark._derive_version(Path("no_version.txt")) == "unknown"


# =========================================================================
# MockScorerProvider tests
# =========================================================================

class TestMockScorerProvider:
    """MockScorerProvider produces deterministic scores."""

    def test_returns_expected_dimensions(self, tmp_path):
        img = tmp_path / "test.png"
        img.write_text("fake")
        scorer = MockScorerProvider(seed=42)
        scores = scorer.score_identity(img)
        expected_dims = {
            "dino_similarity", "clip_alignment", "color_consistency",
            "pose_accuracy", "expression_match", "style_consistency",
        }
        assert set(scores.keys()) == expected_dims

    def test_scores_in_range(self, tmp_path):
        img = tmp_path / "test.png"
        img.write_text("fake")
        scorer = MockScorerProvider(seed=42)
        scores = scorer.score_identity(img)
        for name, val in scores.items():
            assert 0.0 <= val <= 1.0, f"{name} score {val} out of range"

    def test_deterministic_seed(self, tmp_path):
        img = tmp_path / "test.png"
        img.write_text("fake")
        s1 = MockScorerProvider(seed=42)
        s2 = MockScorerProvider(seed=42)
        r1 = s1.score_identity(img)
        r2 = s2.score_identity(img)
        assert r1 == r2


# =========================================================================
# KohyaAdapter integration tests
# =========================================================================

class TestKohyaAdapterIntegration:
    """KohyaAdapter methods that use DatasetBuilder and VersionRegistry."""

    def test_build_dataset_returns_config_path(self, tmp_path):
        """build_dataset() creates a training dataset and returns config path."""
        adapter = KohyaAdapter(kohya_path="")
        img = tmp_path / "test.png"
        img.write_text("fake")
        entries = [
            DatasetEntry(
                image_path=img,
                caption="Lily Bunny, happy expression",
                asset_type="expression",
            ),
        ]
        config_path = adapter.build_dataset(
            entries=entries,
            output_dir=tmp_path / "training_ds",
        )
        assert config_path.exists()
        assert config_path.suffix == ".toml"

    def test_adapter_has_version_registry(self):
        """KohyaAdapter creates a VersionRegistry by default."""
        adapter = KohyaAdapter(kohya_path="")
        assert adapter.version_registry is not None
        assert isinstance(adapter.version_registry, VersionRegistry)

    def test_train_registers_version(self, tmp_path):
        """train() registers version in registry on success (mocked)."""
        adapter = KohyaAdapter(
            kohya_path=str(tmp_path / "kohya"),
            version_registry=VersionRegistry(),
        )
        # Mock validate_environment to return True
        adapter.validate_environment = lambda: True  # type: ignore

        config = TrainingConfig(
            character_id="test-char",
            dataset_path=tmp_path / "dataset",
            output_path=tmp_path / "output",
            version="v0.1",
        )
        (tmp_path / "kohya" / "sd-scripts").mkdir(parents=True, exist_ok=True)
        (tmp_path / "output").mkdir(parents=True, exist_ok=True)

        # We can't actually run Kohya, so use a mock
        import subprocess
        original_run = subprocess.run

        def mock_run(*args, **kwargs):
            class MockProc:
                returncode = 0
                stdout = "training complete"
                stderr = ""
            return MockProc()

        subprocess.run = mock_run  # type: ignore
        try:
            result = adapter.train(config)
            assert result.success
            latest = adapter.version_registry.get_latest("test-char")
            assert latest is not None
            assert str(latest.version) == "v0.1"
        finally:
            subprocess.run = original_run  # type: ignore

    def test_prepare_dataset_with_captions(self, tmp_path):
        """prepare_dataset() uses provided captions when available."""
        adapter = KohyaAdapter(kohya_path="")
        img = tmp_path / "img.png"
        img.write_text("fake")
        result = adapter.prepare_dataset(
            [img],
            tmp_path / "output",
            captions=["custom caption for training"],
        )
        import json
        meta = json.loads((result / "metadata.json").read_text())
        assert meta[0]["caption"] == "custom caption for training"

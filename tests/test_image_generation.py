"""Tests for Phase 8 — AI Image Generation & Visual Asset Pipeline.

Covers:
- ImageMetadata dataclass and defaults
- ImageValidator checks (format, dimensions, metadata)
- UpscalingPipeline (valid methods, scale factor, 4K)
- ThumbnailGenerator (platform presets, fit-to-size, pillarbox)
- ReferenceImageManager (register, get, load, tags)
- PromptVersionManager (register, get_latest, version IDs)
"""

import pytest
from PIL import Image

from src.image_generation import (
    ImageMetadata,
    ImageValidator,
    ValidationResult,
    UpscalingPipeline,
    UpscaleResult,
    ThumbnailGenerator,
    ThumbnailResult,
    ReferenceImageManager,
    ReferenceImage,
    REFERENCE_CATEGORIES,
    PromptVersionManager,
    PromptVersion,
    ConsistencyManager,
    CharacterLock,
    EnvironmentProfile,
    StyleGuide,
    ColorPalette,
    STUDIO_STYLE_CHARACTERISTICS,
    CONTROLLED_PALETTE,
    ModelRoleManager,
    MODEL_RESPONSIBILITIES,
    GENERATION_TYPE_MODEL,
)
from src.image_generation.thumbnail import PLATFORM_SIZES


# ── ImageMetadata Tests ────────────────────────────────────────────────

class TestImageMetadata:
    def test_defaults(self):
        meta = ImageMetadata()
        assert meta.image_id == ""
        assert meta.approval_status == "pending"
        assert meta.revision == 1

    def test_to_dict_roundtrip(self):
        meta = ImageMetadata(
            image_id="IMG_001",
            episode="S01E01",
            model="flux",
            seed=42,
            width=1024,
            height=1024,
        )
        d = meta.to_dict()
        restored = ImageMetadata.from_dict(d)
        assert restored.image_id == "IMG_001"
        assert restored.model == "flux"
        assert restored.seed == 42

    def test_fill_defaults_sets_date(self):
        meta = ImageMetadata()
        meta.fill_defaults()
        assert meta.generation_date != ""

    def test_fill_defaults_sets_aspect_ratio(self):
        meta = ImageMetadata(width=1024, height=1024)
        meta.fill_defaults()
        assert meta.aspect_ratio == "1:1"

        meta2 = ImageMetadata(width=1920, height=1080)
        meta2.fill_defaults()
        assert meta2.aspect_ratio == "16:9"

        meta3 = ImageMetadata(width=1080, height=1920)
        meta3.fill_defaults()
        assert meta3.aspect_ratio == "9:16"

    def test_fill_defaults_does_not_override_existing(self):
        meta = ImageMetadata(aspect_ratio="4:3", width=800, height=600)
        meta.fill_defaults()
        assert meta.aspect_ratio == "4:3"

    def test_is_complete(self):
        meta = ImageMetadata(image_id="X", model="flux", generation_date="2025-01-01")
        assert meta.is_complete()

    def test_is_complete_false(self):
        meta = ImageMetadata()
        assert not meta.is_complete()

    def test_character_ids_default_list(self):
        meta = ImageMetadata()
        assert meta.character_ids == []


# ── ImageValidator Tests ───────────────────────────────────────────────

class TestImageValidator:
    def test_validate_format_valid(self, rgb_image):
        validator = ImageValidator()
        assert validator.validate_format(rgb_image)

    def test_validate_format_invalid(self, rgb_image):
        validator = ImageValidator()
        bw = rgb_image.convert("L")
        assert not validator.validate_format(bw)

    def test_validate_dimensions_valid(self, rgb_image):
        validator = ImageValidator()
        assert validator.validate_dimensions(rgb_image)

    def test_validate_dimensions_too_small(self, rgb_image):
        validator = ImageValidator()
        tiny = Image.new("RGB", (1, 1))
        assert not validator.validate_dimensions(tiny)

    def test_validate_aspect_ratio_valid(self, rgb_image):
        validator = ImageValidator()
        assert validator.validate_aspect_ratio(rgb_image)

    def test_validate_aspect_ratio_extreme(self, rgb_image):
        validator = ImageValidator()
        extreme = Image.new("RGB", (10000, 1))
        assert not validator.validate_aspect_ratio(extreme)

    def test_validate_resolution_standard(self, rgb_image):
        validator = ImageValidator()
        # Our test image is 640x480, below 1024 minimum for production
        # But test with a valid size
        valid = Image.new("RGB", (1024, 1024))
        assert validator.validate_resolution_standard(valid)

    def test_validate_resolution_standard_too_small(self, rgb_image):
        validator = ImageValidator()
        assert not validator.validate_resolution_standard(rgb_image)

    def test_validate_image_passes_all(self):
        validator = ImageValidator()
        img = Image.new("RGB", (1024, 1024))
        meta = ImageMetadata(image_id="X", model="flux", generation_date="2025-01-01", width=1024, height=1024, prompt_version="V1")
        meta.fill_defaults()
        result = validator.validate_image(img, meta)
        assert result.passed, result.errors

    def test_validate_image_fails_on_small(self):
        validator = ImageValidator()
        img = Image.new("RGB", (10, 10))
        result = validator.validate_image(img)
        assert not result.passed

    def test_validation_result_summary(self):
        result = ValidationResult(passed=False, checks={"a": True, "b": False})
        assert "1/2 checks passed" in result.summary()

    def test_validation_result_no_checks(self):
        result = ValidationResult()
        assert result.summary() == "No checks performed"

    def test_failed_checks(self):
        result = ValidationResult(checks={"a": True, "b": False})
        assert result.failed_checks() == ["b"]

    def test_validate_metadata_missing_fields(self):
        validator = ImageValidator()
        meta = ImageMetadata()
        result = validator.validate_metadata(meta)
        assert not result.passed
        assert result.errors


# ── UpscalingPipeline Tests ────────────────────────────────────────────

class TestUpscalingPipeline:
    def test_upscale_by_factor(self, rgb_image):
        pipeline = UpscalingPipeline()
        result = pipeline.upscale(rgb_image, scale_factor=2.0)
        assert result.success
        assert result.upscaled is not None
        assert result.upscaled.size == (1280, 960)

    def test_upscale_to_target_width(self, rgb_image):
        pipeline = UpscalingPipeline()
        result = pipeline.upscale(rgb_image, target_width=800)
        assert result.success
        assert result.upscaled.size[0] == 800

    def test_upscale_to_exact_dimensions(self, rgb_image):
        pipeline = UpscalingPipeline()
        result = pipeline.upscale(rgb_image, target_width=100, target_height=100)
        assert result.success
        assert result.upscaled.size == (100, 100)

    def test_upscale_invalid_method(self, rgb_image):
        pipeline = UpscalingPipeline()
        result = pipeline.upscale(rgb_image, method="invalid")
        assert not result.success
        assert "Unsupported method" in result.error

    def test_upscale_negative_dimensions(self, rgb_image):
        pipeline = UpscalingPipeline()
        result = pipeline.upscale(rgb_image, target_width=-100)
        assert not result.success

    def test_upscale_to_4k(self, rgb_image):
        pipeline = UpscalingPipeline()
        result = pipeline.upscale_to_4k(rgb_image)
        assert result.success
        assert result.target_size == (3840, 2160)

    def test_upscale_original_size_preserved(self, rgb_image):
        pipeline = UpscalingPipeline()
        original_size = rgb_image.size
        result = pipeline.upscale(rgb_image, scale_factor=2.0)
        assert result.original_size == original_size

    def test_upscale_different_methods(self, rgb_image):
        pipeline = UpscalingPipeline()
        for method in ["nearest", "bilinear", "bicubic", "lanczos"]:
            result = pipeline.upscale(rgb_image, scale_factor=1.5, method=method)
            assert result.success, f"{method} failed"


# ── ThumbnailGenerator Tests ───────────────────────────────────────────

class TestThumbnailGenerator:
    def test_generate_youtube_thumbnail(self, rgb_image):
        generator = ThumbnailGenerator()
        result = generator.generate(rgb_image, "youtube_thumbnail")
        assert result.success
        assert result.platform == "youtube_thumbnail"
        assert result.size == (1280, 720)
        assert result.thumbnail is not None

    def test_generate_tiktok(self, rgb_image):
        generator = ThumbnailGenerator()
        result = generator.generate(rgb_image, "tiktok")
        assert result.success
        assert result.size == (1080, 1920)

    def test_generate_unknown_platform(self, rgb_image):
        generator = ThumbnailGenerator()
        result = generator.generate(rgb_image, "nonexistent")
        assert not result.success
        assert "Unknown platform" in result.error

    def test_generate_all(self, rgb_image):
        generator = ThumbnailGenerator()
        results = generator.generate_all(rgb_image)
        assert len(results) == len(PLATFORM_SIZES)
        for platform, result in results.items():
            assert result.success, f"{platform}: {result.error}"

    def test_generate_all_subset(self, rgb_image):
        generator = ThumbnailGenerator()
        results = generator.generate_all(rgb_image, platforms=["youtube_thumbnail", "tiktok"])
        assert len(results) == 2
        assert results["youtube_thumbnail"].success
        assert results["tiktok"].success

    def test_thumbnail_pillarbox_letterbox(self, rgb_image):
        generator = ThumbnailGenerator()
        square = Image.new("RGB", (100, 100), color=(255, 0, 0))
        result = generator.generate(square, "youtube_thumbnail")
        assert result.success
        assert result.thumbnail.size == (1280, 720)


# ── ReferenceImageManager Tests ────────────────────────────────────────

class TestReferenceImageManager:
    def test_register_and_get(self):
        mgr = ReferenceImageManager()
        ref = ReferenceImage(name="lily-bunny", category="characters", source="test")
        mgr.register(ref)
        assert mgr.get("characters", "lily-bunny") is ref

    def test_get_nonexistent(self):
        mgr = ReferenceImageManager()
        assert mgr.get("characters", "nonexistent") is None

    def test_register_invalid_category(self):
        mgr = ReferenceImageManager()
        ref = ReferenceImage(name="test", category="invalid")
        with pytest.raises(ValueError, match="Unknown category"):
            mgr.register(ref)

    def test_get_by_category(self):
        mgr = ReferenceImageManager()
        mgr.register(ReferenceImage(name="a", category="characters"))
        mgr.register(ReferenceImage(name="b", category="characters"))
        mgr.register(ReferenceImage(name="c", category="environments"))
        assert len(mgr.get_by_category("characters")) == 2
        assert len(mgr.get_by_category("environments")) == 1

    def test_get_by_tags(self):
        mgr = ReferenceImageManager()
        mgr.register(ReferenceImage(name="a", category="characters", tags=["happy", "lily"]))
        mgr.register(ReferenceImage(name="b", category="characters", tags=["sad", "ben"]))
        results = mgr.get_by_tags(["lily"])
        assert len(results) == 1
        assert results[0].name == "a"

    def test_convenience_getters(self):
        mgr = ReferenceImageManager()
        mgr.register(ReferenceImage(name="lily", category="characters"))
        mgr.register(ReferenceImage(name="park", category="environments"))
        mgr.register(ReferenceImage(name="wave", category="poses"))
        assert mgr.get_character_reference("lily") is not None
        assert mgr.get_environment_reference("park") is not None
        assert mgr.get_pose_reference("wave") is not None
        assert mgr.get_expression_reference("nonexistent") is None

    def test_count(self):
        mgr = ReferenceImageManager()
        assert mgr.count() == 0
        mgr.register(ReferenceImage(name="a", category="characters"))
        assert mgr.count() == 1

    def test_list_categories(self):
        mgr = ReferenceImageManager()
        assert mgr.list_categories() == REFERENCE_CATEGORIES

    def test_load_image_nonexistent(self):
        mgr = ReferenceImageManager()
        ref = ReferenceImage(name="test", category="characters")
        assert mgr.load_image(ref) is None


# ── PromptVersionManager Tests ─────────────────────────────────────────

class TestPromptVersionManager:
    def test_register_and_get(self):
        mgr = PromptVersionManager()
        vid = mgr.create_version("a cute bunny", "character", model="flux")
        assert vid.startswith("PROMPT_CHARA_V1")
        version = mgr.get(vid)
        assert version is not None
        assert version.prompt_text == "a cute bunny"

    def test_get_latest(self):
        mgr = PromptVersionManager()
        mgr.create_version("v1", "character", model="flux")
        mgr.create_version("v2", "character", model="flux")
        latest = mgr.get_latest("character")
        assert latest.prompt_text == "v2"

    def test_get_latest_nonexistent(self):
        mgr = PromptVersionManager()
        assert mgr.get_latest("nonexistent") is None

    def test_list_by_category(self):
        mgr = PromptVersionManager()
        mgr.create_version("v1", "character")
        mgr.create_version("v2", "environment")
        mgr.create_version("v3", "character")
        char_versions = mgr.list_by_category("character")
        assert len(char_versions) == 2

    def test_list_all(self):
        mgr = PromptVersionManager()
        mgr.create_version("v1", "character")
        mgr.create_version("v2", "environment")
        assert len(mgr.list_all()) == 2

    def test_create_version_with_parent(self):
        mgr = PromptVersionManager()
        parent_id = mgr.create_version("original", "character")
        child_id = mgr.create_version("refined", "character", parent_version=parent_id)
        child = mgr.get(child_id)
        assert child.parent_version == parent_id

    def test_version_auto_id_increment(self):
        mgr = PromptVersionManager()
        v1 = mgr.create_version("a", "environment")
        v2 = mgr.create_version("b", "environment")
        v3 = mgr.create_version("c", "character")
        assert v1 == "PROMPT_ENVIR_V1"
        assert v2 == "PROMPT_ENVIR_V2"
        assert v3 == "PROMPT_CHARA_V1"

    def test_create_version_sets_date(self):
        mgr = PromptVersionManager()
        vid = mgr.create_version("test", "character")
        v = mgr.get(vid)
        assert v.created_at != ""

    def test_count(self):
        mgr = PromptVersionManager()
        assert mgr.count() == 0
        mgr.create_version("a", "character")
        mgr.create_version("b", "environment")
        assert mgr.count() == 2

    def test_register_directly(self):
        mgr = PromptVersionManager()
        v = PromptVersion(prompt_text="test", category="character")
        mgr.register(v)
        assert v.version_id.startswith("PROMPT_CHARA_V1")
        assert mgr.count() == 1

    def test_get_nonexistent(self):
        mgr = PromptVersionManager()
        assert mgr.get("nonexistent") is None


# ── Character / Environment / Style Locking Tests ───────────────────────

class TestCharacterLock:
    def test_defaults(self):
        lock = CharacterLock()
        assert lock.locked is False
        assert lock.reference_images == []

    def test_check_missing_references(self):
        lock = CharacterLock()
        assert lock.check()["has_reference_images"] is False

    def test_check_complete(self):
        lock = CharacterLock(
            reference_images=["refs/lily_front.png"],
            identity_lora="lora/lily.safetensors",
            approved_color_palette="pastels",
            approved_costumes=["dress_a", "dress_b"],
        )
        assert all(lock.check().values())

    def test_is_locked_requires_flag(self):
        lock = CharacterLock(
            reference_images=["refs/lily_front.png"],
            identity_lora="lora/lily.safetensors",
            approved_color_palette="pastels",
            approved_costumes=["dress_a"],
            locked=True,
        )
        assert lock.is_locked() is True

    def test_is_locked_false_when_incomplete(self):
        lock = CharacterLock(locked=True)
        assert lock.is_locked() is False


class TestEnvironmentProfile:
    def test_is_complete(self):
        profile = EnvironmentProfile(
            environment_id="ENV_001",
            master_image="env/maple_park.png",
            layout_map="env/maple_park_layout.png",
            lighting_presets=["morning", "afternoon"],
            weather_presets=["sunny", "rainy"],
            color_palette="natural_greens",
            object_placement_rules=["bench_left", "tree_right"],
        )
        assert profile.is_complete() is True

    def test_is_complete_missing_fields(self):
        profile = EnvironmentProfile(environment_id="ENV_001")
        assert profile.is_complete() is False


class TestStyleGuide:
    def test_studio_characteristics(self):
        assert "soft_lighting" in STUDIO_STYLE_CHARACTERISTICS
        assert len(STUDIO_STYLE_CHARACTERISTICS) == 7

    def test_controlled_palette(self):
        assert "pastels" in CONTROLLED_PALETTE

    def test_characteristic_keys(self):
        guide = StyleGuide()
        keys = guide.characteristic_keys()
        assert "clean_backgrounds" in keys

    def test_contains_characteristic(self):
        guide = StyleGuide()
        assert guide.contains_characteristic("rounded_geometry")
        assert not guide.contains_characteristic("photorealistic")


class TestConsistencyManager:
    def test_lock_and_get_character(self):
        mgr = ConsistencyManager()
        lock = CharacterLock(
            character_id="lily",
            reference_images=["refs/lily.png"],
            identity_lora="lora/lily.safetensors",
            approved_color_palette="pastels",
            approved_costumes=["dress_a"],
        )
        mgr.lock_character(lock)
        assert mgr.get_character_lock("lily") is lock
        assert mgr.locked_character_count() == 1

    def test_validate_character_unregistered(self):
        mgr = ConsistencyManager()
        result = mgr.validate_character("ghost")
        assert result["registered"] is False

    def test_unlock_character(self):
        mgr = ConsistencyManager()
        lock = CharacterLock(character_id="lily")
        mgr.lock_character(lock)
        assert mgr.unlock_character("lily") is True
        assert lock.locked is False
        assert mgr.unlock_character("ghost") is False

    def test_register_and_validate_environment(self):
        mgr = ConsistencyManager()
        profile = EnvironmentProfile(
            environment_id="maple_park",
            master_image="env/maple_park.png",
            layout_map="env/layout.png",
            lighting_presets=["morning"],
            weather_presets=["sunny"],
            color_palette="natural_greens",
            object_placement_rules=["bench_left"],
        )
        mgr.register_environment(profile)
        assert mgr.get_environment("maple_park") is profile
        assert mgr.environment_count() == 1
        assert mgr.validate_environment("maple_park")["has_master_image"] is True

    def test_validate_environment_unregistered(self):
        mgr = ConsistencyManager()
        assert mgr.validate_environment("ghost")["registered"] is False

    def test_style_guide_default(self):
        mgr = ConsistencyManager()
        assert mgr.style_guide().name == "Studio Style Guide"

    def test_validate_style_all_met(self):
        mgr = ConsistencyManager()
        satisfied = {
            "soft_lighting": True,
            "rounded_geometry": True,
            "friendly_proportions": True,
            "bright_pastel_colors": True,
            "minimal_visual_noise": True,
            "large_readable_shapes": True,
            "clean_backgrounds": True,
            "controlled_palette": True,
            "no_oversaturation": True,
        }
        result = mgr.validate_style(satisfied)
        assert result["all_style_characteristics_met"] is True

    def test_validate_style_partial(self):
        mgr = ConsistencyManager()
        result = mgr.validate_style({"soft_lighting": True, "controlled_palette": True})
        assert result["all_style_characteristics_met"] is False

    def test_enforce_combined(self):
        mgr = ConsistencyManager()
        lock = CharacterLock(
            character_id="lily",
            reference_images=["r.png"],
            identity_lora="lora.safetensors",
            approved_color_palette="pastels",
            approved_costumes=["dress"],
        )
        mgr.lock_character(lock)
        result = mgr.enforce(character_id="lily", style_satisfied={})
        assert result["all_locked"] is False
        assert "character_locked" in result


# ── Model Role Tests ────────────────────────────────────────────────────

class TestModelRoleManager:
    def test_models_present(self):
        mgr = ModelRoleManager()
        models = mgr.list_models()
        assert "flux" in models
        assert "sdxl" in models
        assert "pony" in models

    def test_purpose(self):
        mgr = ModelRoleManager()
        assert "production" in mgr.purpose("flux").lower()
        assert mgr.purpose("sdxl") == "Batch generation, concepts, environments"
        assert "stylized" in mgr.purpose("pony").lower()

    def test_recommended_model(self):
        mgr = ModelRoleManager()
        assert mgr.recommended_model("environment") == "sdxl"
        assert mgr.recommended_model("character_portrait") == "flux"
        assert mgr.recommended_model("expression_sheet") == "pony"

    def test_recommended_model_unknown(self):
        mgr = ModelRoleManager()
        assert mgr.recommended_model("unknown_type") == "flux"

    def test_is_responsible(self):
        mgr = ModelRoleManager()
        assert mgr.is_responsible("sdxl", "environment") is True
        assert mgr.is_responsible("flux", "environment") is False

    def test_responsibilities(self):
        mgr = ModelRoleManager()
        resp = mgr.responsibilities()
        assert "flux" in resp
        assert len(resp) == 3

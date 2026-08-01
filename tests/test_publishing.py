"""Tests for Phase 11 — Publishing, Distribution & Channel Management System.

Covers all 12 engine modules and supporting dataclasses.
"""

import pytest

from src.publishing import (
    PublishStatus, Visibility, ComplianceResult,
    Channel, Series, Season, TitleVariant, KeywordEntry,
    Playlist, ReleaseSchedule, ContentVariant, ABTest,
    AnalyticsSnapshot, PublicationRecord,
    MetadataEngine, TitleGenerator, DescriptionEngine, KeywordEngine,
    BrandingEngine, BrandProfile, ComplianceEngine,
    PlaylistEngine, SchedulingEngine, ReleaseCalendar,
    ThumbnailStrategy, ContentVariantEngine,
    PublishingLocalizationEngine, LocalizedPublication,
    PublishingEngine,
    AnalyticsEngine, EducationalAnalyticsEngine,
    PublishingArchiveEngine,
    ChannelManager,
    NotificationEngine, Notification,
    LifecycleManager,
    PublishingDashboard,
)


# ── Model Tests ─────────────────────────────────────────────────────────

class TestChannel:
    def test_defaults(self):
        c = Channel()
        assert c.channel_id == ""
        assert c.platform == "youtube"
        assert c.language == "en"

    def test_full_init(self):
        c = Channel(channel_id="CH_001", name="Lily Kids", platform="youtube")
        assert c.channel_id == "CH_001"
        assert c.name == "Lily Kids"


class TestSeries:
    def test_defaults(self):
        s = Series()
        assert s.age_group == "2-5"
        assert s.curriculum == []

    def test_full_init(self):
        s = Series(series_id="SR_001", name="Colors", curriculum=["colors", "shapes"])
        assert s.series_id == "SR_001"
        assert len(s.curriculum) == 2


class TestSeason:
    def test_defaults(self):
        s = Season()
        assert s.number == 1
        assert s.episode_count == 0

    def test_full_init(self):
        s = Season(season_id="SE_1", series_id="SR_001", number=2, episode_count=10)
        assert s.number == 2
        assert s.episode_count == 10


class TestTitleVariant:
    def test_defaults(self):
        t = TitleVariant()
        assert t.kind == "primary"
        assert t.score == 0.0
        assert t.language == "en"


class TestKeywordEntry:
    def test_defaults(self):
        k = KeywordEntry()
        assert k.category == "general"
        assert k.weight == 1.0


class TestPlaylist:
    def test_defaults(self):
        p = Playlist()
        assert p.episode_count() == 0

    def test_episode_count(self):
        p = Playlist(playlist_id="PL_1", episode_ids=["E1", "E2"])
        assert p.episode_count() == 2

    def test_add_episode(self):
        p = Playlist(playlist_id="PL_1")
        p.add_episode("E1")
        p.add_episode("E1")
        assert p.episode_count() == 1

    def test_full_init(self):
        p = Playlist(playlist_id="PL_1", name="Learn Numbers", topic="numbers")
        assert p.name == "Learn Numbers"


class TestReleaseSchedule:
    def test_defaults(self):
        s = ReleaseSchedule()
        assert s.platform == "youtube"
        assert s.visibility == Visibility.PUBLIC
        assert s.is_premiere is False

    def test_full_init(self):
        s = ReleaseSchedule(episode_id="E1", publish_date="2026-08-01", publish_time="09:00")
        assert s.publish_date == "2026-08-01"
        assert s.publish_time == "09:00"


class TestContentVariant:
    def test_defaults(self):
        v = ContentVariant()
        assert v.kind == ""
        assert v.platform == ""


class TestABTest:
    def test_defaults(self):
        t = ABTest()
        assert t.status == "running"
        assert t.metric == "ctr"


class TestAnalyticsSnapshot:
    def test_defaults(self):
        s = AnalyticsSnapshot()
        assert s.views == 0
        assert s.engagement_rate == 0.0

    def test_engagement_rate(self):
        s = AnalyticsSnapshot(views=100, likes=10, comments=5, shares=5)
        assert s.engagement_rate == 0.2

    def test_engagement_rate_zero_views(self):
        s = AnalyticsSnapshot()
        assert s.engagement_rate == 0.0


class TestPublicationRecord:
    def test_defaults(self):
        r = PublicationRecord()
        assert r.status == PublishStatus.DRAFT
        assert r.version == 1

    def test_full_init(self):
        r = PublicationRecord(episode_id="E1", channel_id="CH_1", platform="youtube")
        assert r.episode_id == "E1"


# ── Enum Value Tests ────────────────────────────────────────────────────

class TestEnumValues:
    def test_publish_status(self):
        assert len(PublishStatus) == 7

    def test_visibility(self):
        assert len(Visibility) == 4

    def test_compliance_result(self):
        assert len(ComplianceResult) == 3


# ── MetadataEngine Tests ────────────────────────────────────────────────

class TestMetadataEngine:
    def test_generate(self):
        engine = MetadataEngine()
        meta = engine.generate(
            episode_id="EP_001",
            title="Colors",
            series="Colors Series",
            learning_objective="Identify colors",
            age_group="2-5",
        )
        assert meta["episode_id"] == "EP_001"
        assert meta["title"] == "Colors"
        assert meta["hashtags"] == []

    def test_generate_hashtags(self):
        engine = MetadataEngine()
        meta = engine.generate(
            episode_id="EP_001",
            title="Colors",
            curriculum_tags=["learn colors", "numbers"],
            keywords=["preschool"],
        )
        assert "#learncolors" in meta["hashtags"]
        assert "#preschool" in meta["hashtags"]

    def test_generate_defaults(self):
        engine = MetadataEngine()
        meta = engine.generate(episode_id="EP_001")
        assert meta["characters"] == []
        assert meta["copyright"].startswith("©")

    def test_validate_completeness_full(self):
        engine = MetadataEngine()
        meta = engine.generate(
            episode_id="EP_001",
            title="Colors",
            learning_objective="Learn colors",
            age_group="2-5",
            language="en",
            keywords=["colors"],
        )
        result = engine.validate_completeness(meta)
        assert result["passed"], result["errors"]
        assert result["score"] == 100.0

    def test_validate_completeness_incomplete(self):
        engine = MetadataEngine()
        result = engine.validate_completeness({})
        assert not result["passed"]
        assert len(result["errors"]) > 0

    def test_hashtags_no_duplicates(self):
        engine = MetadataEngine()
        meta = engine.generate(
            episode_id="EP_001",
            curriculum_tags=["colors", "colors"],
            keywords=["colors"],
        )
        assert meta["hashtags"].count("#colors") == 1


# ── TitleGenerator Tests ────────────────────────────────────────────────

class TestTitleGenerator:
    def test_generate_titles(self):
        gen = TitleGenerator()
        titles = gen.generate_titles("Colors", "Lily Bunny")
        assert len(titles) == 4
        kinds = [t.kind for t in titles]
        assert "primary" in kinds
        assert "seo" in kinds
        assert "short" in kinds

    def test_generate_primary_title(self):
        gen = TitleGenerator()
        titles = gen.generate_titles("Colors", "Lily Bunny")
        primary = next(t for t in titles if t.kind == "primary")
        assert primary.title == "Learn Colors with Lily Bunny!"

    def test_generate_seo_title(self):
        gen = TitleGenerator()
        titles = gen.generate_titles("Colors", "Lily Bunny", age_group="2-5", format="Learning Video")
        seo = next(t for t in titles if t.kind == "seo")
        assert "Preschool" in seo.title or "2-5" in seo.title

    def test_score_title_short(self):
        gen = TitleGenerator()
        score = gen.score_title("Colors Song!")
        assert score > 0

    def test_score_title_too_long(self):
        gen = TitleGenerator()
        long_title = "A" * 200
        score = gen.score_title(long_title)
        assert score < 40

    def test_select_best(self):
        gen = TitleGenerator()
        variants = [
            TitleVariant(title="low", score=10),
            TitleVariant(title="high", score=90),
        ]
        assert gen.select_best(variants).title == "high"

    def test_select_best_empty(self):
        gen = TitleGenerator()
        assert gen.select_best([]).title == ""


# ── DescriptionEngine Tests ─────────────────────────────────────────────

class TestDescriptionEngine:
    def test_build_description(self):
        engine = DescriptionEngine()
        desc = engine.build_description(
            summary="Learn colors with Lily",
            objective="Identify primary colors",
            age_group="2-5",
            series="Colors Series",
        )
        assert "Learning Objective" in desc
        assert "Ages: 2-5" in desc
        assert "subscribe" in desc.lower()
        assert "All rights reserved" in desc

    def test_build_description_with_extras(self):
        engine = DescriptionEngine()
        desc = engine.build_description(
            summary="Learn colors",
            objective="Identify colors",
            highlights=["First highlight", "Second highlight"],
            playlist_links=["https://youtube.com/playlist"],
            website="https://example.com",
            social="https://x.com/studio",
        )
        assert "First highlight" in desc
        assert "youtube.com/playlist" in desc
        assert "example.com" in desc
        assert "x.com/studio" in desc

    def test_validate_full(self):
        engine = DescriptionEngine()
        desc = engine.build_description(
            summary="Learn colors with Lily",
            objective="Identify primary colors",
        )
        result = engine.validate(desc)
        assert result["passed"], result["errors"]

    def test_validate_empty(self):
        engine = DescriptionEngine()
        result = engine.validate("")
        assert not result["passed"]


# ── KeywordEngine Tests ─────────────────────────────────────────────────

class TestKeywordEngine:
    def test_suggest(self):
        engine = KeywordEngine()
        keywords = engine.suggest(["colors"])
        assert "learn colors" in keywords
        assert "color songs" in keywords

    def test_suggest_unknown_topic(self):
        engine = KeywordEngine()
        keywords = engine.suggest(["nonexistent_topic"])
        assert len(keywords) > 0

    def test_suggest_limit(self):
        engine = KeywordEngine()
        keywords = engine.suggest(["colors", "numbers"], limit=4)
        assert len(keywords) <= 4

    def test_add_keyword(self):
        engine = KeywordEngine()
        engine.add_keyword("bunny songs", "animals")
        assert "bunny songs" in engine.keywords_for_category("animals")

    def test_add_keyword_new_category(self):
        engine = KeywordEngine()
        engine.add_keyword("custom", "new_category")
        assert "new_category" in engine.list_categories()

    def test_add_keyword_no_duplicate(self):
        engine = KeywordEngine()
        engine.add_keyword("kids", "general")
        general = engine.keywords_for_category("general")
        assert general.count("kids") == 1

    def test_all_keywords(self):
        engine = KeywordEngine()
        keywords = engine.all_keywords()
        assert len(keywords) > 10

    def test_list_categories(self):
        engine = KeywordEngine()
        categories = engine.list_categories()
        assert "colors" in categories
        assert "numbers" in categories

    def test_keywords_for_category_unknown(self):
        engine = KeywordEngine()
        assert engine.keywords_for_category("unknown") == []


# ── BrandingEngine Tests ────────────────────────────────────────────────

class TestBrandingEngine:
    def test_register_and_get(self):
        engine = BrandingEngine()
        profile = BrandProfile(brand_id="BR_1", name="Lily Kids")
        engine.register(profile)
        assert engine.get("BR_1").name == "Lily Kids"

    def test_get_nonexistent(self):
        engine = BrandingEngine()
        assert engine.get("missing").brand_id == ""

    def test_verify_branding_full(self):
        engine = BrandingEngine()
        profile = BrandProfile(
            brand_id="BR_1",
            studio_logo="logo.png",
            series_logo="series.png",
            colors=["#FF0000", "#00FF00"],
            fonts=["Comic Sans"],
            intro_asset="intro.mp4",
            outro_asset="outro.mp4",
            end_screen_asset="endscreen.png",
            website="https://example.com",
            social_links=["https://youtube.com/@lilykids"],
        )
        result = engine.verify_branding(profile)
        assert result["passed"], result["errors"]

    def test_verify_branding_incomplete(self):
        engine = BrandingEngine()
        result = engine.verify_branding(BrandProfile())
        assert not result["passed"]
        assert len(result["errors"]) > 0

    def test_list_brands(self):
        engine = BrandingEngine()
        engine.register(BrandProfile(brand_id="BR_1"))
        engine.register(BrandProfile(brand_id="BR_2"))
        assert len(engine.list_brands()) == 2


# ── ComplianceEngine Tests ──────────────────────────────────────────────

class TestComplianceEngine:
    def test_check_coppa_child_directed(self):
        engine = ComplianceEngine()
        result = engine.check_coppa({"age_group": "2-5"})
        assert result["passed"], result["errors"]

    def test_check_coppa_not_child_directed(self):
        engine = ComplianceEngine()
        result = engine.check_coppa({"age_group": "13-17"})
        assert not result["passed"]

    def test_check_age_appropriate_safe(self):
        engine = ComplianceEngine()
        result = engine.check_age_appropriate({"age_group": "2-5"}, "TV-Y")
        assert result["passed"], result["errors"]

    def test_check_age_appropriate_unsafe_rating(self):
        engine = ComplianceEngine()
        result = engine.check_age_appropriate({"age_group": "2-5"}, "R")
        assert not result["passed"]

    def test_check_copyright_ok(self):
        engine = ComplianceEngine()
        assert engine.check_copyright(ownership=True, music_licensed=True)["passed"]

    def test_check_copyright_not_owned(self):
        engine = ComplianceEngine()
        result = engine.check_copyright(ownership=False, music_licensed=True)
        assert not result["passed"]

    def test_check_copyright_music_not_licensed(self):
        engine = ComplianceEngine()
        result = engine.check_copyright(ownership=True, music_licensed=False)
        assert not result["passed"]

    def test_check_thumbnail_compliance(self):
        engine = ComplianceEngine()
        assert engine.check_thumbnail_compliance(True)["passed"]
        assert not engine.check_thumbnail_compliance(False)["passed"]

    def test_full_compliance_check_passing(self):
        engine = ComplianceEngine()
        result = engine.full_compliance_check({"age_group": "2-5"}, "TV-Y")
        assert result["passed"]
        assert all(result["results"].values())

    def test_full_compliance_check_failing(self):
        engine = ComplianceEngine()
        result = engine.full_compliance_check({"age_group": "13-17"}, "TV-Y")
        assert not result["passed"]


# ── PlaylistEngine Tests ────────────────────────────────────────────────

class TestPlaylistEngine:
    def test_create(self):
        engine = PlaylistEngine()
        pl = engine.create("PL_1", "Learn Numbers", topic="numbers")
        assert pl.playlist_id == "PL_1"
        assert pl.topic == "numbers"

    def test_get(self):
        engine = PlaylistEngine()
        engine.create("PL_1", "Learn Colors")
        assert engine.get("PL_1").name == "Learn Colors"

    def test_get_nonexistent(self):
        engine = PlaylistEngine()
        assert engine.get("missing").playlist_id == ""

    def test_assign_episode(self):
        engine = PlaylistEngine()
        engine.create("PL_1", "Learn Colors")
        assert engine.assign_episode("PL_1", "EP_001")
        assert engine.get("PL_1").episode_count() == 1

    def test_assign_episode_nonexistent_playlist(self):
        engine = PlaylistEngine()
        assert not engine.assign_episode("missing", "EP_001")

    def test_remove_episode(self):
        engine = PlaylistEngine()
        engine.create("PL_1", "Learn Colors")
        engine.assign_episode("PL_1", "EP_001")
        assert engine.remove_episode("PL_1", "EP_001")
        assert engine.get("PL_1").episode_count() == 0

    def test_remove_episode_not_present(self):
        engine = PlaylistEngine()
        engine.create("PL_1", "Learn Colors")
        assert not engine.remove_episode("PL_1", "MISSING")

    def test_list_playlists(self):
        engine = PlaylistEngine()
        engine.create("PL_1", "A")
        engine.create("PL_2", "B")
        assert len(engine.list_playlists()) == 2

    def test_playlist_count(self):
        engine = PlaylistEngine()
        assert engine.playlist_count() == 0
        engine.create("PL_1", "A")
        assert engine.playlist_count() == 1

    def test_suggest_for_episode(self):
        engine = PlaylistEngine()
        engine.create("PL_1", "Learn Colors", topic="colors")
        engine.create("PL_2", "Learn Numbers", topic="numbers")
        suggestions = engine.suggest_for_episode("EP_001", ["colors"])
        assert len(suggestions) == 1
        assert suggestions[0].playlist_id == "PL_1"


# ── SchedulingEngine Tests ──────────────────────────────────────────────

class TestSchedulingEngine:
    def test_create_schedule(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01", "09:00")
        assert sched.episode_id == "EP_001"
        assert sched.publish_date == "2026-08-01"
        assert sched.publish_time == "09:00"
        assert sched.schedule_id.startswith("SCH_")

    def test_create_schedule_premiere(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01", is_premiere=True)
        assert sched.is_premiere is True

    def test_create_schedule_custom_visibility(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01", visibility=Visibility.UNLISTED)
        assert sched.visibility == Visibility.UNLISTED

    def test_get(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01")
        assert engine.get(sched.schedule_id) is sched

    def test_get_nonexistent(self):
        engine = SchedulingEngine()
        assert engine.get("missing").schedule_id == ""

    def test_list_schedules(self):
        engine = SchedulingEngine()
        engine.create_schedule("EP_001", "2026-08-01")
        engine.create_schedule("EP_002", "2026-08-02")
        assert len(engine.list_schedules()) == 2

    def test_schedules_for_episode(self):
        engine = SchedulingEngine()
        engine.create_schedule("EP_001", "2026-08-01", platform="youtube")
        engine.create_schedule("EP_001", "2026-08-02", platform="tiktok")
        engine.create_schedule("EP_002", "2026-08-03")
        assert len(engine.schedules_for_episode("EP_001")) == 2

    def test_schedules_for_date(self):
        engine = SchedulingEngine()
        engine.create_schedule("EP_001", "2026-08-01")
        engine.create_schedule("EP_002", "2026-08-01")
        engine.create_schedule("EP_003", "2026-08-02")
        assert len(engine.schedules_for_date("2026-08-01")) == 2

    def test_count(self):
        engine = SchedulingEngine()
        assert engine.count() == 0
        engine.create_schedule("EP_001", "2026-08-01")
        assert engine.count() == 1


# ── ThumbnailStrategy Tests ─────────────────────────────────────────────

class TestThumbnailStrategy:
    def test_evaluate_default(self):
        strategy = ThumbnailStrategy()
        result = strategy.evaluate()
        assert result["total_score"] == pytest.approx(0.5)
        assert "emotion" in result

    def test_evaluate_high_scores(self):
        strategy = ThumbnailStrategy()
        result = strategy.evaluate(
            eye_contact=1.0, facial_expression=1.0, brightness=1.0,
            contrast=1.0, readability=1.0, emotion=1.0, educational_focus=1.0,
        )
        assert result["total_score"] == pytest.approx(1.0)

    def test_select_best(self):
        strategy = ThumbnailStrategy()
        candidates = [
            strategy.evaluate(eye_contact=0.3),
            strategy.evaluate(eye_contact=0.9),
        ]
        best = strategy.select_best(candidates)
        assert best["eye_contact"] == 0.9

    def test_select_best_empty(self):
        strategy = ThumbnailStrategy()
        assert strategy.select_best([]) is None


# ── ContentVariantEngine Tests ──────────────────────────────────────────

class TestContentVariantEngine:
    def test_plan_variants(self):
        engine = ContentVariantEngine()
        variants = engine.plan_variants("EP_001", 300.0)
        assert len(variants) == 13
        kinds = [v.kind for v in variants]
        assert "full" in kinds
        assert "shorts" in kinds
        assert "trailer" in kinds
        assert "gif" in kinds
        assert "facebook_clip" in kinds
        assert "thumbnail" in kinds
        assert "preview" in kinds
        assert "newsletter" in kinds
        assert "website" in kinds
        assert "bts" in kinds

    def test_plan_variants_durations(self):
        engine = ContentVariantEngine()
        variants = engine.plan_variants("EP_001", 300.0)
        by_kind = {v.kind: v for v in variants}
        assert by_kind["full"].duration == 300.0
        assert by_kind["shorts"].duration == pytest.approx(45.0)
        assert by_kind["gif"].duration == pytest.approx(15.0)

    def test_plan_variants_resolution(self):
        engine = ContentVariantEngine()
        variants = engine.plan_variants("EP_001", 300.0)
        by_kind = {v.kind: v for v in variants}
        assert by_kind["full"].resolution == "1920x1080"
        assert by_kind["shorts"].resolution == "1080x1920"

    def test_plan_variant_single(self):
        engine = ContentVariantEngine()
        variant = engine.plan_variant("EP_001", 300.0, "trailer")
        assert variant is not None
        assert variant.kind == "trailer"
        assert variant.platform == "youtube"

    def test_plan_variant_unknown(self):
        engine = ContentVariantEngine()
        assert engine.plan_variant("EP_001", 300.0, "unknown") is None

    def test_list_variant_kinds(self):
        engine = ContentVariantEngine()
        assert len(engine.list_variant_kinds()) == 13


# ── PublishingLocalizationEngine Tests ──────────────────────────────────

class TestPublishingLocalizationEngine:
    def test_list_languages(self):
        engine = PublishingLocalizationEngine()
        langs = engine.list_languages()
        assert "en" in langs
        assert len(langs) == 10

    def test_is_supported(self):
        engine = PublishingLocalizationEngine()
        assert engine.is_supported("es")
        assert not engine.is_supported("xx")

    def test_create_package(self):
        engine = PublishingLocalizationEngine()
        pkg = engine.create_package("EP_001", "es", title="Colores", thumbnail="thumb_es.jpg")
        assert pkg is not None
        assert pkg.language == "es"
        assert pkg.title == "Colores"
        assert pkg.thumbnail == "thumb_es.jpg"
        assert pkg.subtitle_file == "EP_001.es.srt"

    def test_create_package_unsupported(self):
        engine = PublishingLocalizationEngine()
        assert engine.create_package("EP_001", "xx") is None

    def test_create_package_default_title(self):
        engine = PublishingLocalizationEngine()
        pkg = engine.create_package("EP_001", "fr")
        assert pkg.title == "[fr] EP_001"

    def test_localize_title(self):
        engine = PublishingLocalizationEngine()
        assert engine.localize_title("Colors", "es") == "[es] Colors"

    def test_localize_title_unsupported(self):
        engine = PublishingLocalizationEngine()
        assert engine.localize_title("Colors", "xx") == "Colors"

    def test_localize_description(self):
        engine = PublishingLocalizationEngine()
        desc = engine.localize_description("Hello world", "es")
        assert "Translated to Spanish" in desc


# ── PublishingEngine Tests ──────────────────────────────────────────────

class TestPublishingEngine:
    def test_create_record(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1", "youtube", "Colors")
        assert record.episode_id == "EP_001"
        assert record.channel_id == "CH_1"
        assert record.status == PublishStatus.DRAFT
        assert record.title == "Colors"
        assert record.record_id.startswith("PUB_")

    def test_get(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert engine.get(record.record_id) is record

    def test_get_nonexistent(self):
        engine = PublishingEngine()
        assert engine.get("missing").record_id == ""

    def test_records_for_episode(self):
        engine = PublishingEngine()
        engine.create_record("EP_001", "CH_1", "youtube")
        engine.create_record("EP_001", "CH_1", "tiktok")
        engine.create_record("EP_002", "CH_1")
        assert len(engine.records_for_episode("EP_001")) == 2

    def test_approve(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert engine.approve(record.record_id)
        assert record.status == PublishStatus.APPROVED

    def test_approve_nonexistent(self):
        engine = PublishingEngine()
        assert not engine.approve("missing")

    def test_schedule(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert engine.schedule(record.record_id, "2026-08-01T09:00:00")
        assert record.status == PublishStatus.SCHEDULED
        assert record.scheduled_at == "2026-08-01T09:00:00"

    def test_publish_from_approved(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        engine.approve(record.record_id)
        assert engine.publish(record.record_id, "https://youtube.com/watch?v=abc")
        assert record.status == PublishStatus.PUBLISHED
        assert record.published_at != ""
        assert record.video_url == "https://youtube.com/watch?v=abc"

    def test_publish_from_draft_fails(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert not engine.publish(record.record_id)

    def test_publish_nonexistent(self):
        engine = PublishingEngine()
        assert not engine.publish("missing")

    def test_update(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        engine.approve(record.record_id)
        engine.publish(record.record_id)
        assert engine.update(record.record_id)
        assert record.status == PublishStatus.UPDATED
        assert record.version == 2

    def test_update_before_publish_fails(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert not engine.update(record.record_id)

    def test_archive(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert engine.archive(record.record_id)
        assert record.status == PublishStatus.ARCHIVED

    def test_set_visibility(self):
        engine = PublishingEngine()
        record = engine.create_record("EP_001", "CH_1")
        assert engine.set_visibility(record.record_id, Visibility.PRIVATE)
        assert record.visibility == Visibility.PRIVATE

    def test_set_visibility_nonexistent(self):
        engine = PublishingEngine()
        assert not engine.set_visibility("missing", Visibility.PRIVATE)

    def test_prepare_publish_package(self):
        engine = PublishingEngine()
        package = engine.prepare_publish_package(
            episode_id="EP_001",
            topic="colors",
            character="Lily Bunny",
            objective="Identify primary colors",
            series="Colors Series",
        )
        assert package["episode_id"] == "EP_001"
        assert len(package["titles"]) == 4
        assert package["selected_title"] != ""
        assert package["metadata"]["learning_objective"] == "Identify primary colors"
        assert "Learning Objective" in package["description"]


# ── AnalyticsEngine Tests ───────────────────────────────────────────────

class TestAnalyticsEngine:
    def test_record(self):
        engine = AnalyticsEngine()
        snap = engine.record(AnalyticsSnapshot(episode_id="EP_001", views=100))
        assert snap.timestamp != ""
        assert len(engine.snapshots_for("EP_001")) == 1

    def test_snapshots_for(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001"))
        engine.record(AnalyticsSnapshot(episode_id="EP_001"))
        engine.record(AnalyticsSnapshot(episode_id="EP_002"))
        assert len(engine.snapshots_for("EP_001")) == 2

    def test_latest_for(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001", views=100, timestamp="2026-01-01"))
        engine.record(AnalyticsSnapshot(episode_id="EP_001", views=200, timestamp="2026-01-02"))
        assert engine.latest_for("EP_001").views == 200

    def test_latest_for_none(self):
        engine = AnalyticsEngine()
        assert engine.latest_for("EP_001") is None

    def test_total_views(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001", views=100))
        engine.record(AnalyticsSnapshot(episode_id="EP_002", views=50))
        assert engine.total_views() == 150

    def test_average_retention(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001", audience_retention=0.5))
        engine.record(AnalyticsSnapshot(episode_id="EP_002", audience_retention=0.7))
        assert engine.average_retention() == pytest.approx(0.6)

    def test_average_retention_empty(self):
        engine = AnalyticsEngine()
        assert engine.average_retention() == 0.0

    def test_average_ctr(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001", ctr=0.04))
        engine.record(AnalyticsSnapshot(episode_id="EP_002", ctr=0.08))
        assert engine.average_ctr() == pytest.approx(0.06)

    def test_top_episodes(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001", views=100))
        engine.record(AnalyticsSnapshot(episode_id="EP_002", views=300))
        engine.record(AnalyticsSnapshot(episode_id="EP_003", views=200))
        top = engine.top_episodes()
        assert top[0].episode_id == "EP_002"

    def test_top_episodes_limit(self):
        engine = AnalyticsEngine()
        for i in range(5):
            engine.record(AnalyticsSnapshot(episode_id=f"EP_{i}", views=i * 10))
        assert len(engine.top_episodes(limit=3)) == 3

    def test_educational_metrics(self):
        engine = AnalyticsEngine()
        engine.record(AnalyticsSnapshot(episode_id="EP_001", views=500, audience_retention=0.6,
                                         likes=50, comments=10, shares=10))
        report = engine.educational_metrics({
            "EP_001": {"topic": "colors", "target_age": "2-5", "song_count": 1, "question_count": 3},
        })
        assert "EP_001" in report
        assert report["EP_001"]["views"] == 500
        assert report["EP_001"]["topic"] == "colors"

    def test_create_ab_test(self):
        engine = AnalyticsEngine()
        test = engine.create_ab_test("EP_001", "title", "Title A", "Title B")
        assert test.test_id.startswith("AB_")
        assert test.status == "running"
        assert test.variant_a == "Title A"

    def test_list_ab_tests(self):
        engine = AnalyticsEngine()
        engine.create_ab_test("EP_001", "thumbnail", "A", "B")
        engine.create_ab_test("EP_001", "title", "X", "Y")
        assert len(engine.list_ab_tests()) == 2

    def test_get_ab_test(self):
        engine = AnalyticsEngine()
        test = engine.create_ab_test("EP_001", "title", "A", "B")
        assert engine.get_ab_test(test.test_id) is test

    def test_get_ab_test_nonexistent(self):
        engine = AnalyticsEngine()
        assert engine.get_ab_test("missing").test_id == ""

    def test_conclude_ab_test(self):
        engine = AnalyticsEngine()
        test = engine.create_ab_test("EP_001", "title", "A", "B")
        engine.conclude_ab_test(test.test_id, "a")
        assert test.status == "concluded"


# ── PublishingArchiveEngine Tests ───────────────────────────────────────

class TestPublishingArchiveEngine:
    def test_store(self):
        engine = PublishingArchiveEngine()
        record = PublicationRecord(
            record_id="PUB_1", episode_id="EP_001", channel_id="CH_1",
            status=PublishStatus.PUBLISHED, title="Colors",
        )
        snap = AnalyticsSnapshot(episode_id="EP_001", views=100, ctr=0.05)
        entry = engine.store(record, snap)
        assert entry["episode_id"] == "EP_001"
        assert entry["status"] == "published"
        assert entry["analytics"]["views"] == 100

    def test_history_for(self):
        engine = PublishingArchiveEngine()
        engine.store(PublicationRecord(episode_id="EP_001"))
        engine.store(PublicationRecord(episode_id="EP_001"))
        engine.store(PublicationRecord(episode_id="EP_002"))
        assert len(engine.history_for("EP_001")) == 2

    def test_all_archives(self):
        engine = PublishingArchiveEngine()
        engine.store(PublicationRecord(episode_id="EP_001"))
        assert len(engine.all_archives()) == 1

    def test_count(self):
        engine = PublishingArchiveEngine()
        assert engine.count() == 0
        engine.store(PublicationRecord(episode_id="EP_001"))
        assert engine.count() == 1

    def test_list_episode_ids(self):
        engine = PublishingArchiveEngine()
        engine.store(PublicationRecord(episode_id="EP_001"))
        engine.store(PublicationRecord(episode_id="EP_001"))
        engine.store(PublicationRecord(episode_id="EP_002"))
        ids = engine.list_episode_ids()
        assert len(ids) == 2
        assert "EP_001" in ids


# ── ChannelManager Tests ────────────────────────────────────────────────

class TestChannelManager:
    def test_add_and_get_channel(self):
        manager = ChannelManager()
        channel = Channel(channel_id="CH_1", name="Lily Kids")
        manager.add_channel(channel)
        assert manager.get_channel("CH_1").name == "Lily Kids"

    def test_get_channel_nonexistent(self):
        manager = ChannelManager()
        assert manager.get_channel("missing").channel_id == ""

    def test_list_channels(self):
        manager = ChannelManager()
        manager.add_channel(Channel(channel_id="CH_1"))
        manager.add_channel(Channel(channel_id="CH_2"))
        assert len(manager.list_channels()) == 2

    def test_channel_count(self):
        manager = ChannelManager()
        manager.add_channel(Channel(channel_id="CH_1"))
        assert manager.channel_count() == 1

    def test_add_and_get_series(self):
        manager = ChannelManager()
        series = Series(series_id="SR_1", name="Colors", curriculum=["colors"])
        manager.add_series(series)
        assert manager.get_series("SR_1").name == "Colors"

    def test_list_series(self):
        manager = ChannelManager()
        manager.add_series(Series(series_id="SR_1"))
        manager.add_series(Series(series_id="SR_2"))
        assert len(manager.list_series()) == 2

    def test_add_and_get_season(self):
        manager = ChannelManager()
        season = Season(season_id="SE_1", series_id="SR_1", number=1)
        manager.add_season(season)
        assert manager.get_season("SE_1").series_id == "SR_1"

    def test_seasons_for_series(self):
        manager = ChannelManager()
        manager.add_season(Season(season_id="SE_1", series_id="SR_1"))
        manager.add_season(Season(season_id="SE_2", series_id="SR_1"))
        manager.add_season(Season(season_id="SE_3", series_id="SR_2"))
        assert len(manager.seasons_for_series("SR_1")) == 2

    def test_series_for_topic(self):
        manager = ChannelManager()
        manager.add_series(Series(series_id="SR_1", name="Colors", curriculum=["colors"]))
        manager.add_series(Series(series_id="SR_2", name="Numbers"))
        matches = manager.series_for_topic("colors")
        assert len(matches) == 1
        assert matches[0].series_id == "SR_1"

    def test_age_group_series(self):
        manager = ChannelManager()
        manager.add_series(Series(series_id="SR_1", age_group="2-5"))
        manager.add_series(Series(series_id="SR_2", age_group="6-8"))
        assert len(manager.age_group_series("2-5")) == 1


# ── NotificationEngine Tests ────────────────────────────────────────────

class TestNotificationEngine:
    def test_notify(self):
        engine = NotificationEngine()
        n = engine.notify("upload_complete", "Upload complete!")
        assert n.notification_id.startswith("NOT_")
        assert n.event_type == "upload_complete"
        assert n.read is False
        assert n.created_at != ""

    def test_is_valid_event(self):
        engine = NotificationEngine()
        assert engine.is_valid_event("copyright_claim")
        assert engine.is_valid_event("publishing_failed")
        assert not engine.is_valid_event("invalid_event")

    def test_list_all(self):
        engine = NotificationEngine()
        engine.notify("upload_complete", "msg")
        engine.notify("policy_warning", "msg")
        assert len(engine.list_all()) == 2

    def test_list_unread(self):
        engine = NotificationEngine()
        engine.notify("upload_complete", "msg")
        engine.notify("upload_complete", "msg")
        assert len(engine.list_unread()) == 2

    def test_list_for_episode(self):
        engine = NotificationEngine()
        engine.notify("copyright_claim", "msg", episode_id="EP_001")
        engine.notify("upload_complete", "msg", episode_id="EP_002")
        assert len(engine.list_for_episode("EP_001")) == 1

    def test_mark_read(self):
        engine = NotificationEngine()
        n = engine.notify("upload_complete", "msg")
        assert engine.mark_read(n.notification_id)
        assert n.read is True
        assert len(engine.list_unread()) == 0

    def test_mark_read_nonexistent(self):
        engine = NotificationEngine()
        assert not engine.mark_read("missing")

    def test_mark_all_read(self):
        engine = NotificationEngine()
        engine.notify("upload_complete", "msg")
        engine.notify("monetization_issue", "msg")
        assert engine.mark_all_read() == 2
        assert engine.unread_count() == 0

    def test_count(self):
        engine = NotificationEngine()
        assert engine.count() == 0
        engine.notify("upload_complete", "msg")
        assert engine.count() == 1

    def test_unread_count(self):
        engine = NotificationEngine()
        engine.notify("upload_complete", "msg")
        assert engine.unread_count() == 1


# ── LifecycleManager Tests ──────────────────────────────────────────────

class TestLifecycleManager:
    def test_start(self):
        manager = LifecycleManager()
        lifecycle = manager.start("EP_001")
        assert lifecycle["stage"] == "concept"
        assert len(lifecycle["history"]) == 1

    def test_advance(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        assert manager.advance("EP_001", "production")
        assert manager.get_stage("EP_001") == "production"

    def test_advance_multiple_steps(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        for stage in ["production", "editing", "approved", "scheduled", "published"]:
            assert manager.advance("EP_001", stage)

    def test_advance_unknown_episode(self):
        manager = LifecycleManager()
        assert not manager.advance("MISSING", "production")

    def test_advance_invalid_stage(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        assert not manager.advance("EP_001", "invalid_stage")

    def test_advance_backwards_fails(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        manager.advance("EP_001", "production")
        assert not manager.advance("EP_001", "concept")

    def test_advance_same_stage_fails(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        assert not manager.advance("EP_001", "concept")

    def test_get_stage_unknown(self):
        manager = LifecycleManager()
        assert manager.get_stage("MISSING") == ""

    def test_get_lifecycle(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        assert manager.get_lifecycle("EP_001")["stage"] == "concept"

    def test_get_lifecycle_unknown(self):
        manager = LifecycleManager()
        assert manager.get_lifecycle("MISSING") == {}

    def test_list_all(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        manager.start("EP_002")
        assert len(manager.list_all()) == 2

    def test_count(self):
        manager = LifecycleManager()
        assert manager.count() == 0
        manager.start("EP_001")
        assert manager.count() == 1

    def test_list_by_stage(self):
        manager = LifecycleManager()
        manager.start("EP_001")
        manager.start("EP_002")
        manager.advance("EP_002", "production")
        assert len(manager.list_by_stage("concept")) == 1
        assert len(manager.list_by_stage("production")) == 1


# ── ReleaseCalendar Tests ───────────────────────────────────────────────

class TestReleaseCalendar:
    def test_add_release(self):
        calendar = ReleaseCalendar()
        entry = calendar.add_release("EP_001", "2026-08-01", "weekly")
        assert entry["entry_id"] == "RC_1"
        assert entry["cadence"] == "weekly"
        assert calendar.count() == 1

    def test_add_release_invalid_cadence(self):
        calendar = ReleaseCalendar()
        assert calendar.add_release("EP_001", "2026-08-01", "never") is None

    def test_cadences(self):
        calendar = ReleaseCalendar()
        cadences = calendar.list_cadences()
        assert "daily" in cadences
        assert "weekly" in cadences
        assert "bi_weekly" in cadences
        assert "monthly" in cadences
        assert "holiday_special" in cadences
        assert "season_launch" in cadences
        assert "premiere" in cadences
        assert len(cadences) == 7

    def test_releases_for_cadence(self):
        calendar = ReleaseCalendar()
        calendar.add_release("EP_001", "2026-08-01", "weekly")
        calendar.add_release("EP_002", "2026-08-08", "weekly")
        calendar.add_release("EP_003", "2026-09-01", "monthly")
        assert len(calendar.releases_for_cadence("weekly")) == 2
        assert len(calendar.releases()) == 3

    def test_releases_on_date(self):
        calendar = ReleaseCalendar()
        calendar.add_release("EP_001", "2026-08-01")
        calendar.add_release("EP_002", "2026-08-01")
        calendar.add_release("EP_003", "2026-08-02")
        assert len(calendar.releases_on_date("2026-08-01")) == 2

    def test_upcoming(self):
        calendar = ReleaseCalendar()
        calendar.add_release("EP_001", "2026-08-01", "weekly")
        calendar.add_release("EP_002", "2026-09-01", "monthly")
        calendar.add_release("EP_003", "2026-12-25", "holiday_special")
        upcoming = calendar.upcoming()
        assert len(upcoming) == 1
        assert upcoming[0]["episode_id"] == "EP_001"

    def test_consistent_cadence(self):
        calendar = ReleaseCalendar()
        assert calendar.consistent_cadence("weekly") is False
        calendar.add_release("EP_001", "2026-08-01", "weekly")
        calendar.add_release("EP_002", "2026-08-08", "weekly")
        assert calendar.consistent_cadence("weekly") is True


# ── EducationalAnalyticsEngine Tests ────────────────────────────────────

class TestEducationalAnalyticsEngine:
    def setup_method(self):
        self.engine = EducationalAnalyticsEngine()

    def test_record(self):
        record = self.engine.record("EP_001", "colors", question_count=3)
        assert record["episode_id"] == "EP_001"
        assert record["learning_topic"] == "colors"
        assert record["question_count"] == 3
        assert self.engine.count() == 1

    def test_for_episode(self):
        self.engine.record("EP_001", "colors")
        self.engine.record("EP_002", "numbers")
        assert self.engine.for_episode("EP_001")["learning_topic"] == "colors"
        assert self.engine.for_episode("EP_003") == {}

    def test_topic_performance(self):
        self.engine.record("EP_001", "colors", completion_rate=0.8, replay_rate=0.4, song_count=1, question_count=3)
        self.engine.record("EP_002", "colors", completion_rate=0.6, replay_rate=0.2, song_count=1, question_count=2)
        perf = self.engine.topic_performance("colors")
        assert perf["episode_count"] == 2
        assert perf["average_completion_rate"] == pytest.approx(0.7)
        assert perf["average_replay_rate"] == pytest.approx(0.3)
        assert perf["total_songs"] == 2
        assert perf["total_questions"] == 5

    def test_topic_performance_empty(self):
        perf = self.engine.topic_performance("colors")
        assert perf["episode_count"] == 0

    def test_list_topics(self):
        self.engine.record("EP_001", "colors")
        self.engine.record("EP_002", "colors")
        self.engine.record("EP_003", "numbers")
        topics = self.engine.list_topics()
        assert len(topics) == 2
        assert "colors" in topics
        assert "numbers" in topics

    def test_popular_topics(self):
        self.engine.record("EP_001", "colors")
        self.engine.record("EP_002", "colors")
        self.engine.record("EP_003", "numbers")
        popular = self.engine.popular_topics()
        assert popular[0]["learning_topic"] == "colors"
        assert popular[0]["episode_count"] == 2

    def test_popular_topics_empty(self):
        assert self.engine.popular_topics() == []


# ── Compliance Expansion Tests ──────────────────────────────────────────

class TestComplianceExpansion:
    def test_platform_policies_supported(self):
        engine = ComplianceEngine()
        result = engine.check_platform_policies("youtube")
        assert result["passed"], result["errors"]
        assert result["checks"]["platform_supported"] is True

    def test_platform_policies_unsupported(self):
        engine = ComplianceEngine()
        result = engine.check_platform_policies("mystery-site")
        assert not result["passed"]
        assert "platform_supported" in result["errors"]

    def test_community_guidelines_clean(self):
        engine = ComplianceEngine()
        result = engine.check_community_guidelines({
            "title": "Learn Colors",
            "description": "Fun preschool learning",
            "keywords": ["colors", "shapes"],
        })
        assert result["passed"], result["errors"]

    def test_community_guidelines_violent(self):
        engine = ComplianceEngine()
        result = engine.check_community_guidelines({
            "title": "Fighting game violence",
            "description": "",
            "keywords": ["weapon"],
        })
        assert not result["passed"]
        assert "no_violent_content" in result["errors"]

    def test_full_check_includes_expanded(self):
        engine = ComplianceEngine()
        result = engine.full_compliance_check({"age_group": "2-5"}, "TV-Y")
        assert result["passed"]
        assert result["results"]["platform_policies"] is True
        assert result["results"]["community_guidelines"] is True


# ── Scheduling Expansion Tests ──────────────────────────────────────────

class TestSchedulingExpansion:
    def test_create_schedule_language(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01", language="es")
        assert sched.language == "es"

    def test_create_schedule_embargo(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01", embargo_date="2026-07-30")
        assert sched.embargo_date == "2026-07-30"

    def test_create_schedule_language_and_embargo_defaults(self):
        engine = SchedulingEngine()
        sched = engine.create_schedule("EP_001", "2026-08-01")
        assert sched.language == "en"
        assert sched.embargo_date == ""


# ── Localization Expansion Tests ────────────────────────────────────────

class TestLocalizationExpansion:
    def test_create_package_audio_track(self):
        engine = PublishingLocalizationEngine()
        pkg = engine.create_package("EP_001", "es")
        assert pkg is not None
        assert pkg.audio_track == "EP_001.es.m4a"

    def test_audio_track_field_exists(self):
        assert LocalizedPublication().audio_track == ""


# ── ABTest Winner Tests ─────────────────────────────────────────────────

class TestABTestWinner:
    def test_conclude_records_winner(self):
        engine = AnalyticsEngine()
        test = engine.create_ab_test("EP_001", "title", "A", "B")
        engine.conclude_ab_test(test.test_id, "b")
        assert test.status == "concluded"
        assert test.winner == "b"

    def test_default_winner(self):
        assert ABTest().winner == ""

    def test_conclude_unknown(self):
        engine = AnalyticsEngine()
        result = engine.conclude_ab_test("missing", "a")
        assert result.test_id == ""


# ── AnalyticsSnapshot Expansion Tests ───────────────────────────────────

class TestAnalyticsSnapshotExpansion:
    def test_new_fields_defaults(self):
        s = AnalyticsSnapshot()
        assert s.playlist_adds == 0
        assert s.traffic_sources == []
        assert s.geography == {}
        assert s.language == "en"
        assert s.device_type == ""
        assert s.platform == "youtube"
        assert s.revenue == 0.0

    def test_new_fields_initialized(self):
        s = AnalyticsSnapshot(
            views=100,
            playlist_adds=5,
            traffic_sources=[{"source": "search", "percent": 60}],
            geography={"US": 70},
            language="en",
            device_type="mobile",
            platform="youtube",
            revenue=25.5,
        )
        assert s.playlist_adds == 5
        assert s.geography["US"] == 70
        assert s.revenue == 25.5


# ── Archive Expansion Tests ─────────────────────────────────────────────

class TestArchiveExpansion:
    def test_store_with_subtitles(self):
        engine = PublishingArchiveEngine()
        entry = engine.store(PublicationRecord(episode_id="EP_001"), subtitles=["en.srt", "es.srt"])
        assert entry["subtitles"] == ["en.srt", "es.srt"]

    def test_store_no_subtitles(self):
        engine = PublishingArchiveEngine()
        entry = engine.store(PublicationRecord(episode_id="EP_001"))
        assert entry["subtitles"] == []


# ── PublishingEngine validate_ready Tests ───────────────────────────────

class TestValidateReady:
    def _ready_engine(self):
        engine = PublishingEngine()
        engine.create_record("EP_001", "CH_1")
        engine.approve("PUB_1")
        return engine

    def test_ready_approved_record(self):
        engine = self._ready_engine()
        result = engine.validate_ready(
            "PUB_1",
            thumbnail_approved=True,
            metadata_generated=True,
            localization_complete=True,
            compliance_passed=True,
            schedule_assigned=True,
        )
        assert result["passed"]
        assert result["errors"] == []

    def test_ready_missing_checks(self):
        engine = self._ready_engine()
        result = engine.validate_ready("PUB_1", thumbnail_approved=True)
        assert not result["passed"]
        assert "metadata_generated" in result["errors"]
        assert "localization_complete" in result["errors"]
        assert "compliance_passed" in result["errors"]
        assert "schedule_assigned" in result["errors"]

    def test_ready_unknown_record(self):
        engine = PublishingEngine()
        result = engine.validate_ready("MISSING")
        assert not result["passed"]
        assert result["errors"] == ["record_not_found"]

    def test_ready_draft_record_fails(self):
        engine = PublishingEngine()
        engine.create_record("EP_001", "CH_1")
        result = engine.validate_ready(
            "PUB_1",
            thumbnail_approved=True,
            metadata_generated=True,
            localization_complete=True,
            compliance_passed=True,
            schedule_assigned=True,
        )
        assert not result["passed"]
        assert "record_approved" in result["errors"]


# ── PublishingDashboard Tests ───────────────────────────────────────────

class TestPublishingDashboard:
    def test_overview_sections(self):
        dashboard = PublishingDashboard()
        overview = dashboard.overview()
        assert set(overview.keys()) == {
            "upcoming_releases", "publishing_queue", "localization_status",
            "copyright_alerts", "analytics_overview", "trending_episodes",
            "failed_uploads", "performance_reports", "revenue_summary",
            "automation_status",
        }

    def test_setters(self):
        dashboard = PublishingDashboard()
        dashboard.set_upcoming_releases([{"episode_id": "EP_001"}])
        dashboard.set_publishing_queue([{"task": "upload"}])
        dashboard.set_localization_status([{"language": "es"}])
        dashboard.add_copyright_alert({"message": "claim"})
        dashboard.add_failed_upload({"episode_id": "EP_002"})
        overview = dashboard.overview()
        assert len(overview["upcoming_releases"]) == 1
        assert len(overview["publishing_queue"]) == 1
        assert len(overview["copyright_alerts"]) == 1
        assert len(overview["failed_uploads"]) == 1

    def test_trending_episodes(self):
        dashboard = PublishingDashboard()
        dashboard.set_analytics_overview({"episodes": [
            {"episode_id": "EP_001", "views": 100},
            {"episode_id": "EP_002", "views": 300},
        ]})
        trending = dashboard.trending_episodes()
        assert trending[0]["episode_id"] == "EP_002"

    def test_revenue_and_automation(self):
        dashboard = PublishingDashboard()
        dashboard.set_analytics_overview({"revenue": 100.5})
        dashboard.set_publishing_queue([{"task": "upload"}, {"task": "schedule"}])
        assert dashboard.revenue_summary() == 100.5
        status = dashboard.automation_status()
        assert status["queue_count"] == 2
        assert status["failed_uploads"] == 0

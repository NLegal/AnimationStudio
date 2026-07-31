from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PublishStatus(str, Enum):
    DRAFT = "draft"
    INTERNAL_REVIEW = "internal_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    UPDATED = "updated"
    ARCHIVED = "archived"


class Visibility(str, Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    PREMIERE = "premiere"


class ComplianceResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PENDING = "pending"


@dataclass
class Channel:
    channel_id: str = ""
    name: str = ""
    brand: str = ""
    platform: str = "youtube"
    language: str = "en"
    region: str = "US"
    subscribers: int = 0


@dataclass
class Series:
    series_id: str = ""
    name: str = ""
    description: str = ""
    age_group: str = "2-5"
    curriculum: list[str] = field(default_factory=list)
    playlist_id: str = ""


@dataclass
class Season:
    season_id: str = ""
    series_id: str = ""
    number: int = 1
    name: str = ""
    episode_count: int = 0


@dataclass
class TitleVariant:
    title: str = ""
    kind: str = "primary"  # primary, seo, short, localized
    score: float = 0.0
    language: str = "en"


@dataclass
class KeywordEntry:
    keyword: str = ""
    category: str = "general"
    language: str = "en"
    weight: float = 1.0


@dataclass
class Playlist:
    playlist_id: str = ""
    name: str = ""
    series_id: str = ""
    topic: str = ""
    episode_ids: list[str] = field(default_factory=list)

    def episode_count(self) -> int:
        return len(self.episode_ids)

    def add_episode(self, episode_id: str) -> None:
        if episode_id not in self.episode_ids:
            self.episode_ids.append(episode_id)


@dataclass
class ReleaseSchedule:
    schedule_id: str = ""
    episode_id: str = ""
    platform: str = "youtube"
    publish_date: str = ""
    publish_time: str = ""
    timezone: str = "UTC"
    language: str = "en"
    visibility: Visibility = Visibility.PUBLIC
    is_premiere: bool = False
    embargo_date: str = ""


@dataclass
class ContentVariant:
    variant_id: str = ""
    episode_id: str = ""
    kind: str = ""  # full, shorts, tiktok, reel, trailer, teaser, gif
    platform: str = ""
    duration: float = 0.0
    resolution: str = ""
    asset_path: str = ""


@dataclass
class ABTest:
    test_id: str = ""
    episode_id: str = ""
    attribute: str = ""  # title, description, thumbnail, publish_time
    variant_a: str = ""
    variant_b: str = ""
    status: str = "running"
    metric: str = "ctr"


@dataclass
class AnalyticsSnapshot:
    episode_id: str = ""
    views: int = 0
    watch_time_seconds: float = 0.0
    average_view_duration: float = 0.0
    audience_retention: float = 0.0
    ctr: float = 0.0
    subscribers_gained: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    timestamp: str = ""

    @property
    def engagement_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return round((self.likes + self.comments + self.shares) / self.views, 4)


@dataclass
class PublicationRecord:
    record_id: str = ""
    episode_id: str = ""
    channel_id: str = ""
    platform: str = "youtube"
    status: PublishStatus = PublishStatus.DRAFT
    visibility: Visibility = Visibility.PUBLIC
    title: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    thumbnail: str = ""
    scheduled_at: str = ""
    published_at: str = ""
    video_url: str = ""
    version: int = 1

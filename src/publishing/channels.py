from __future__ import annotations

from .models import Channel, Series, Season


class ChannelManager:
    def __init__(self):
        self._channels: dict[str, Channel] = {}
        self._series: dict[str, Series] = {}
        self._seasons: dict[str, Season] = {}

    def add_channel(self, channel: Channel) -> Channel:
        self._channels[channel.channel_id] = channel
        return channel

    def get_channel(self, channel_id: str) -> Channel:
        return self._channels.get(channel_id, Channel())

    def list_channels(self) -> list[Channel]:
        return list(self._channels.values())

    def channel_count(self) -> int:
        return len(self._channels)

    def add_series(self, series: Series) -> Series:
        self._series[series.series_id] = series
        return series

    def get_series(self, series_id: str) -> Series:
        return self._series.get(series_id, Series())

    def list_series(self) -> list[Series]:
        return list(self._series.values())

    def series_count(self) -> int:
        return len(self._series)

    def add_season(self, season: Season) -> Season:
        self._seasons[season.season_id] = season
        return season

    def get_season(self, season_id: str) -> Season:
        return self._seasons.get(season_id, Season())

    def seasons_for_series(self, series_id: str) -> list[Season]:
        return [s for s in self._seasons.values() if s.series_id == series_id]

    def season_count(self) -> int:
        return len(self._seasons)

    def series_for_topic(self, topic: str) -> list[Series]:
        return [s for s in self._series.values() if topic in s.curriculum or topic in s.name.lower()]

    def age_group_series(self, age_group: str) -> list[Series]:
        return [s for s in self._series.values() if s.age_group == age_group]

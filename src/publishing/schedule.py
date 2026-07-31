from __future__ import annotations

from .models import Playlist, ReleaseSchedule, Visibility


class PlaylistEngine:
    def __init__(self):
        self._playlists: dict[str, Playlist] = {}

    def create(self, playlist_id: str, name: str, series_id: str = "", topic: str = "") -> Playlist:
        playlist = Playlist(
            playlist_id=playlist_id,
            name=name,
            series_id=series_id,
            topic=topic,
        )
        self._playlists[playlist_id] = playlist
        return playlist

    def get(self, playlist_id: str) -> Playlist:
        return self._playlists.get(playlist_id, Playlist())

    def assign_episode(self, playlist_id: str, episode_id: str) -> bool:
        playlist = self._playlists.get(playlist_id)
        if playlist is None:
            return False
        playlist.add_episode(episode_id)
        return True

    def remove_episode(self, playlist_id: str, episode_id: str) -> bool:
        playlist = self._playlists.get(playlist_id)
        if playlist is None:
            return False
        if episode_id in playlist.episode_ids:
            playlist.episode_ids.remove(episode_id)
            return True
        return False

    def list_playlists(self) -> list[Playlist]:
        return list(self._playlists.values())

    def playlist_count(self) -> int:
        return len(self._playlists)

    def suggest_for_episode(self, episode_id: str, topics: list[str]) -> list[Playlist]:
        suggestions: list[Playlist] = []
        for topic in topics:
            for playlist in self._playlists.values():
                if playlist.topic == topic or topic in playlist.name.lower():
                    suggestions.append(playlist)
        return suggestions


class SchedulingEngine:
    def __init__(self):
        self._schedules: dict[str, ReleaseSchedule] = {}
        self._counter = 0

    def create_schedule(
        self,
        episode_id: str,
        publish_date: str,
        publish_time: str = "09:00",
        platform: str = "youtube",
        timezone: str = "UTC",
        visibility: Visibility = Visibility.PUBLIC,
        is_premiere: bool = False,
    ) -> ReleaseSchedule:
        self._counter += 1
        schedule = ReleaseSchedule(
            schedule_id=f"SCH_{self._counter}",
            episode_id=episode_id,
            platform=platform,
            publish_date=publish_date,
            publish_time=publish_time,
            timezone=timezone,
            visibility=visibility,
            is_premiere=is_premiere,
        )
        self._schedules[schedule.schedule_id] = schedule
        return schedule

    def get(self, schedule_id: str) -> ReleaseSchedule:
        return self._schedules.get(schedule_id, ReleaseSchedule())

    def list_schedules(self) -> list[ReleaseSchedule]:
        return list(self._schedules.values())

    def schedules_for_episode(self, episode_id: str) -> list[ReleaseSchedule]:
        return [s for s in self._schedules.values() if s.episode_id == episode_id]

    def schedules_for_date(self, publish_date: str) -> list[ReleaseSchedule]:
        return [s for s in self._schedules.values() if s.publish_date == publish_date]

    def count(self) -> int:
        return len(self._schedules)

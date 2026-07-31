from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Notification:
    notification_id: str = ""
    event_type: str = ""
    message: str = ""
    severity: str = "info"
    episode_id: str = ""
    created_at: str = ""
    read: bool = False


class NotificationEngine:
    EVENT_TYPES = {
        "upload_complete",
        "publishing_failed",
        "copyright_claim",
        "thumbnail_rejected",
        "policy_warning",
        "performance_milestone",
        "monetization_issue",
    }

    def __init__(self):
        self._notifications: list[Notification] = []
        self._counter = 0

    def notify(self, event_type: str, message: str, episode_id: str = "", severity: str = "info") -> Notification:
        self._counter += 1
        notification = Notification(
            notification_id=f"NOT_{self._counter}",
            event_type=event_type,
            message=message,
            severity=severity,
            episode_id=episode_id,
            created_at=datetime.now().isoformat(),
        )
        self._notifications.append(notification)
        return notification

    def is_valid_event(self, event_type: str) -> bool:
        return event_type in self.EVENT_TYPES

    def list_all(self) -> list[Notification]:
        return list(self._notifications)

    def list_unread(self) -> list[Notification]:
        return [n for n in self._notifications if not n.read]

    def list_for_episode(self, episode_id: str) -> list[Notification]:
        return [n for n in self._notifications if n.episode_id == episode_id]

    def mark_read(self, notification_id: str) -> bool:
        for n in self._notifications:
            if n.notification_id == notification_id:
                n.read = True
                return True
        return False

    def mark_all_read(self) -> int:
        count = 0
        for n in self._notifications:
            if not n.read:
                n.read = True
                count += 1
        return count

    def count(self) -> int:
        return len(self._notifications)

    def unread_count(self) -> int:
        return len(self.list_unread())

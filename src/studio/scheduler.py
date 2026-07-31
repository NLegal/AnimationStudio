from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ScheduleEvent:
    event_id: str = ""
    event_type: str = ""
    subject: str = ""
    scheduled_for: str = ""
    recurring: str = "once"
    payload: dict = field(default_factory=dict)
    created_at: str = ""


class StudioScheduler:
    def __init__(self):
        self._events: dict[str, ScheduleEvent] = {}
        self._counter = 0

    def schedule(
        self,
        event_type: str,
        subject: str,
        scheduled_for: str,
        recurring: str = "once",
        payload: dict | None = None,
    ) -> ScheduleEvent:
        self._counter += 1
        event = ScheduleEvent(
            event_id=f"SCHEVT_{self._counter}",
            event_type=event_type,
            subject=subject,
            scheduled_for=scheduled_for,
            recurring=recurring,
            payload=payload or {},
            created_at=datetime.now().isoformat(),
        )
        self._events[event.event_id] = event
        return event

    def schedule_daily(self, event_type: str, subject: str) -> ScheduleEvent:
        return self.schedule(event_type, subject, datetime.now().isoformat(), recurring="daily")

    def schedule_weekly(self, event_type: str, subject: str) -> ScheduleEvent:
        return self.schedule(event_type, subject, datetime.now().isoformat(), recurring="weekly")

    def schedule_monthly(self, event_type: str, subject: str) -> ScheduleEvent:
        return self.schedule(event_type, subject, datetime.now().isoformat(), recurring="monthly")

    def get(self, event_id: str) -> ScheduleEvent:
        return self._events.get(event_id, ScheduleEvent())

    def events_on(self, scheduled_for: str) -> list[ScheduleEvent]:
        return [e for e in self._events.values() if e.scheduled_for == scheduled_for]

    def events_of_type(self, event_type: str) -> list[ScheduleEvent]:
        return [e for e in self._events.values() if e.event_type == event_type]

    def recurring_events(self) -> list[ScheduleEvent]:
        return [e for e in self._events.values() if e.recurring != "once"]

    def list_all(self) -> list[ScheduleEvent]:
        return list(self._events.values())

    def count(self) -> int:
        return len(self._events)

    def cancel(self, event_id: str) -> bool:
        return self._events.pop(event_id, None) is not None

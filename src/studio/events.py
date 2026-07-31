from __future__ import annotations
from datetime import datetime

from .models import StudioEvent, EventType


class EventBus:
    def __init__(self):
        self._subscribers: dict[EventType, list[str]] = {}
        self._events: list[StudioEvent] = []
        self._counter = 0

    def subscribe(self, event_type: EventType, subscriber: str) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if subscriber not in self._subscribers[event_type]:
            self._subscribers[event_type].append(subscriber)

    def unsubscribe(self, event_type: EventType, subscriber: str) -> bool:
        if event_type not in self._subscribers:
            return False
        if subscriber in self._subscribers[event_type]:
            self._subscribers[event_type].remove(subscriber)
            return True
        return False

    def publish(self, event_type: EventType, source: str = "", payload: dict | None = None) -> StudioEvent:
        self._counter += 1
        event = StudioEvent(
            event_id=f"EVT_{self._counter}",
            event_type=event_type,
            source=source,
            payload=payload or {},
            timestamp=datetime.now().isoformat(),
        )
        self._events.append(event)
        return event

    def subscribers_for(self, event_type: EventType) -> list[str]:
        return list(self._subscribers.get(event_type, []))

    def events_for(self, event_type: EventType) -> list[StudioEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def events_from(self, source: str) -> list[StudioEvent]:
        return [e for e in self._events if e.source == source]

    def all_events(self) -> list[StudioEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events = []
        self._counter = 0

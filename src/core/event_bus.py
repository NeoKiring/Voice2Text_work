from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, DefaultDict


@dataclass(slots=True)
class Event:
    topic: str
    payload: dict[str, Any]
    occurred_at: datetime


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, topic: str, callback: Callable[[Event], None]) -> None:
        self._subscribers[topic].append(callback)

    def publish(self, topic: str, payload: dict[str, Any] | None = None) -> None:
        event = Event(topic=topic, payload=payload or {}, occurred_at=datetime.utcnow())
        for callback in self._subscribers.get(topic, []):
            callback(event)

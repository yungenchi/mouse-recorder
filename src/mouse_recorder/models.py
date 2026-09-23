"""Domain models for recorded mouse actions."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    """Supported mouse event categories."""

    MOVE = "move"
    BUTTON = "button"
    CLICK = "button"  # Backwards-compatible alias.
    SCROLL = "scroll"


@dataclass(slots=True)
class MouseEvent:
    """One mouse action and the delay since the previous action."""

    type: EventType
    timestamp: float
    x: int | None = None
    y: int | None = None
    button: str | None = None
    pressed: bool | None = None
    dx: int = 0
    dy: int = 0

    @property
    def t(self) -> float:
        return self.timestamp

    def to_dict(self) -> dict[str, Any]:
        data = {
            "type": self.type.value,
            "t": round(self.timestamp, 6),
        }
        if self.type is EventType.MOVE:
            data.update(x=self.x, y=self.y)
        elif self.type is EventType.BUTTON:
            data.update(button=self.button, pressed=self.pressed, x=self.x, y=self.y)
        else:
            data.update(x=self.x, y=self.y, dx=self.dx, dy=self.dy)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MouseEvent":
        event_type = data["type"]
        if event_type == "click":
            event_type = "button"
        return cls(
            type=EventType(event_type),
            timestamp=float(data.get("t", data.get("timestamp"))),
            x=data.get("x"),
            y=data.get("y"),
            button=data.get("button"),
            pressed=data.get("pressed"),
            dx=int(data.get("dx", 0)),
            dy=int(data.get("dy", 0)),
        )


@dataclass(slots=True)
class Recording:
    """A named sequence of recorded mouse events."""

    name: str
    events: list[MouseEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    screen: dict[str, int] | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(), compare=False
    )

    @property
    def duration(self) -> float:
        if not self.events:
            return 0.0
        return max(event.timestamp for event in self.events)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "screen": self.screen,
            "duration": round(self.duration, 6),
            "created_at": self.created_at,
            "events": [event.to_dict() for event in self.events],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recording":
        if data.get("version", 1) != 1:
            raise ValueError(f"Unsupported recording version: {data.get('version')}")
        if not isinstance(data.get("events", []), list):
            raise ValueError("Recording events must be a list")
        return cls(
            name=str(data["name"]),
            events=[MouseEvent.from_dict(event) for event in data.get("events", [])],
            metadata=dict(data.get("metadata", {})),
            version=1,
            screen=data.get("screen"),
            created_at=str(data.get("created_at", datetime.now(timezone.utc).isoformat())),
        )

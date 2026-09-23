from mouse_recorder.models import EventType, MouseEvent, Recording
from mouse_recorder.player import Player


def test_player_emits_events_in_order(monkeypatch) -> None:
    emitted = []
    sleeps = []
    recording = Recording(
        name="demo",
        events=[
            MouseEvent(EventType.MOVE, timestamp=1.0),
            MouseEvent(EventType.CLICK, timestamp=3.0),
        ],
    )
    monkeypatch.setattr("mouse_recorder.player.time.sleep", sleeps.append)

    Player(emitted.append).play(recording, speed=2.0)

    assert emitted == recording.events
    assert sleeps == [0.5, 1.5]


def test_player_rejects_invalid_speed() -> None:
    try:
        Player(lambda event: None).play(Recording(name="demo"), speed=0)
    except ValueError:
        pass
    else:
        raise AssertionError("non-positive speed should be rejected")

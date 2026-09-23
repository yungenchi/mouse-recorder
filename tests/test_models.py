from mouse_recorder.models import EventType, MouseEvent, Recording


def test_recording_round_trip() -> None:
    recording = Recording(
        name="demo",
        events=[MouseEvent(EventType.MOVE, timestamp=1.25, x=10, y=20)],
        metadata={"platform": "macOS"},
    )

    restored = Recording.from_dict(recording.to_dict())

    assert restored == recording
    assert restored.duration == 1.25
    assert restored.events[0].t == 1.25


def test_unsupported_version_is_rejected() -> None:
    try:
        Recording.from_dict({"version": 2, "name": "demo", "events": []})
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported versions should be rejected")

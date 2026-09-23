from mouse_recorder.models import Recording
from mouse_recorder.storage import RecordingStore


def test_store_saves_loads_and_lists(tmp_path) -> None:
    store = RecordingStore(tmp_path)
    store.save(Recording(name="demo"))

    assert store.list() == ["demo"]
    assert store.load("demo") == Recording(name="demo")


def test_store_rejects_path_traversal(tmp_path) -> None:
    store = RecordingStore(tmp_path)

    try:
        store.path_for("../outside")
    except ValueError:
        pass
    else:
        raise AssertionError("path traversal should be rejected")


def test_store_deletes_recording(tmp_path) -> None:
    store = RecordingStore(tmp_path)
    store.save(Recording(name="demo"))

    store.delete("demo")

    assert store.list() == []

"""JSON persistence for recordings."""

import json
from pathlib import Path

from .models import Recording


class RecordingStore:
    """Store recordings as one JSON file per recording."""

    def __init__(self, directory: Path | str | None = None) -> None:
        self.directory = Path(directory) if directory else Path.home() / ".mouse-recorder" / "recordings"

    def save(self, recording: Recording) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.path_for(recording.name)
        path.write_text(json.dumps(recording.to_dict(), indent=2) + "\n", encoding="utf-8")
        return path

    def load(self, name: str) -> Recording:
        path = self.path_for(name)
        if not path.exists():
            raise FileNotFoundError(name)
        try:
            return Recording.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'Recording "{name}" is corrupted or invalid') from exc

    def list(self) -> list[str]:
        if not self.directory.exists():
            return []
        return sorted(path.stem for path in self.directory.glob("*.json"))

    def delete(self, name: str) -> None:
        try:
            self.path_for(name).unlink()
        except FileNotFoundError as exc:
            raise FileNotFoundError(name) from exc

    def path_for(self, name: str) -> Path:
        if not name or Path(name).name != name:
            raise ValueError("Recording name must be a simple non-empty filename")
        return self.directory / f"{name}.json"

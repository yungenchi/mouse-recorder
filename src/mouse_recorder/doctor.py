"""Environment and permission diagnostics."""

import platform
import sys
from pathlib import Path


def screen_size() -> dict[str, int] | None:
    """Return the primary display size when the platform exposes it."""
    try:
        from AppKit import NSScreen
        frame = NSScreen.mainScreen().frame()
        return {"width": int(frame.size.width), "height": int(frame.size.height)}
    except (ImportError, AttributeError):
        return None


def run_diagnostics(directory: Path | str | None = None) -> list[str]:
    recording_dir = Path(directory) if directory else Path.home() / ".mouse-recorder" / "recordings"
    lines = [
        f"Platform: {platform.system()}",
        f"Python: {sys.version.split()[0]}",
        f"Recording directory: {recording_dir}",
    ]
    size = screen_size()
    lines.append(f"Screen: {size['width']} x {size['height']}" if size else "Screen: unavailable")
    try:
        from pynput import mouse
        mouse.Controller()
        lines.append("Mouse control: OK")
    except Exception as exc:
        lines.append(f"Mouse control: unavailable ({exc})")
    if platform.system() == "Darwin":
        lines.extend([
            "macOS permissions may require Accessibility access for Terminal or your IDE.",
            "Input Monitoring permission may also be required.",
        ])
    return lines

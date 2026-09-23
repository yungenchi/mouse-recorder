"""Environment and permission diagnostics."""

import platform
import subprocess
import sys
import time
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
        accessibility_ok = macos_accessibility_trusted()
        input_monitoring_ok = macos_input_monitoring_trusted()
        if accessibility_ok:
            lines.append("Accessibility: OK")
        else:
            lines.append("Accessibility: permission required")
        if input_monitoring_ok:
            lines.append("Input Monitoring: OK")
        else:
            lines.append("Input Monitoring: permission required")
        lines.extend([
            "Run doctor to open the required macOS settings if permission is missing.",
        ])
    return lines


def macos_accessibility_trusted() -> bool:
    """Check whether the current executable is trusted by macOS Accessibility."""
    if platform.system() != "Darwin":
        return True
    try:
        from ApplicationServices import AXIsProcessTrusted
        return bool(AXIsProcessTrusted())
    except (ImportError, AttributeError):
        return False


def macos_input_monitoring_trusted() -> bool:
    """Check whether macOS allows this executable to monitor input events."""
    if platform.system() != "Darwin":
        return True
    try:
        from Quartz import CGPreflightListenEventAccess
        return bool(CGPreflightListenEventAccess())
    except (ImportError, AttributeError):
        return False


def open_permission_settings() -> None:
    """Open the macOS privacy panes needed for mouse and keyboard monitoring."""
    if platform.system() != "Darwin":
        raise RuntimeError("Permission settings shortcut is only available on macOS")
    for index, pane in enumerate(("Privacy_Accessibility", "Privacy_ListenEvent")):
        subprocess.Popen([
            "open",
            f"x-apple.systempreferences:com.apple.preference.security?{pane}",
        ])
        if index == 0:
            time.sleep(1.0)

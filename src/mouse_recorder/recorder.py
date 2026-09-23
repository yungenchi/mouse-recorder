"""Capture mouse input into a recording."""

import time
from collections.abc import Callable
from threading import Event

from .models import EventType, MouseEvent, Recording


class Recorder:
    """Record mouse events until ESC is pressed."""

    def __init__(self, clock: Callable[[], float] = time.monotonic, screen: dict[str, int] | None = None) -> None:
        self.clock = clock
        self.screen = screen

    def record(self, name: str, stop_event: Event | None = None) -> Recording:
        try:
            from pynput import keyboard, mouse
        except ImportError as exc:
            raise RuntimeError("pynput is required for recording") from exc

        events: list[MouseEvent] = []
        stopped = stop_event or Event()
        started = self.clock()
        last_move = -float("inf")

        def elapsed() -> float:
            return max(0.0, self.clock() - started)

        def on_move(x: int, y: int) -> None:
            nonlocal last_move
            now = elapsed()
            if now - last_move < 0.01:
                return
            last_move = now
            events.append(MouseEvent(EventType.MOVE, now, x=x, y=y))

        def on_click(x: int, y: int, button: object, pressed: bool) -> None:
            events.append(MouseEvent(EventType.BUTTON, elapsed(), x=x, y=y,
                                     button=getattr(button, "name", str(button)), pressed=pressed))

        def on_scroll(x: int, y: int, dx: int, dy: int) -> None:
            events.append(MouseEvent(EventType.SCROLL, elapsed(), x=x, y=y, dx=dx, dy=dy))

        mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = None
        if stop_event is None:
            def on_press(key: object) -> bool | None:
                if key == keyboard.Key.esc:
                    stopped.set()
                    return False
                return None

            keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener.start()
        if keyboard_listener is not None:
            keyboard_listener.start()
        stopped.wait()
        mouse_listener.stop()
        mouse_listener.join()
        if keyboard_listener is not None:
            keyboard_listener.stop()
            keyboard_listener.join()
        return Recording(name=name, events=events, screen=self.screen)

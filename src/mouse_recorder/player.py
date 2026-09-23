"""Replay recorded mouse events with safe interruption and cleanup."""

import time
from collections.abc import Callable
from threading import Event

from .models import EventType, MouseEvent, Recording


class Player:
    """Replay events through pynput or an injected event callback."""

    def __init__(self, emit: Callable[[MouseEvent], None] | None = None,
                 clock: Callable[[], float] = time.monotonic,
                 sleeper: Callable[[float], None] | None = None,
                 abort_event: Event | None = None,
                 listen_for_abort: bool = True) -> None:
        self.emit = emit
        self.clock = clock
        self.sleeper = sleeper or time.sleep
        self.abort_event = abort_event or Event()
        self.listen_for_abort = listen_for_abort
        self._pressed: set[str] = set()
        self._controller = None

    def play(
        self,
        recording: Recording,
        speed: float = 1.0,
        repeat: int = 1,
        delay: float = 0.0,
        loop: bool = False,
    ) -> None:
        if speed <= 0:
            raise ValueError("Playback speed must be greater than zero")
        if repeat < 1:
            raise ValueError("Playback repeat must be at least one")
        if delay < 0:
            raise ValueError("Playback delay cannot be negative")

        abort_listener = None
        try:
            if self.emit is None:
                self._setup_controller()
                if self.listen_for_abort:
                    abort_listener = self._start_abort_listener()
            if delay and not self._wait_until(self.clock() + delay):
                return
            cycle = 0
            while loop or cycle < repeat:
                started = self.clock()
                for event in recording.events:
                    if not self._wait_until(started + event.timestamp / speed):
                        return
                    self._emit(event)
                cycle += 1
                if not recording.events:
                    return
        finally:
            if abort_listener is not None:
                abort_listener.stop()
                abort_listener.join()
            self._release_buttons()

    def _wait_until(self, target: float) -> bool:
        if self.emit is not None:
            remaining = target - self.clock()
            if remaining > 0 and not self.abort_event.is_set():
                self.sleeper(round(remaining, 3))
            return not self.abort_event.is_set()
        while True:
            remaining = target - self.clock()
            if remaining <= 0:
                return not self.abort_event.is_set()
            self.sleeper(min(remaining, 0.01))
            if self.abort_event.is_set():
                return False

    def _setup_controller(self) -> None:
        from pynput import mouse
        self._controller = mouse.Controller()

    def _start_abort_listener(self):
        from pynput import keyboard

        def on_press(key: object) -> bool | None:
            if key == keyboard.Key.esc:
                self.abort_event.set()
                return False
            return None

        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        return listener

    def _emit(self, event: MouseEvent) -> None:
        if self.emit is not None:
            self.emit(event)
            return
        from pynput.mouse import Button

        if event.x is not None and event.y is not None:
            self._controller.position = (event.x, event.y)
        if event.type is EventType.BUTTON:
            button = getattr(Button, event.button or "left")
            if event.pressed:
                self._controller.press(button)
                self._pressed.add(event.button or "left")
            else:
                self._controller.release(button)
                self._pressed.discard(event.button or "left")
        elif event.type is EventType.SCROLL:
            self._controller.scroll(event.dx, event.dy)

    def _release_buttons(self) -> None:
        if self._controller is None:
            self._pressed.clear()
            return
        from pynput.mouse import Button
        for name in tuple(self._pressed):
            self._controller.release(getattr(Button, name, Button.left))
        self._pressed.clear()

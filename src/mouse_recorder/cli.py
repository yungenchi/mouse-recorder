"""User-facing Typer CLI."""

import json
from pathlib import Path
from threading import Event, Lock, Thread

import typer
from rich.console import Console
from rich.table import Table

from .doctor import run_diagnostics, screen_size
from .player import Player
from .recorder import Recorder
from .storage import RecordingStore

app = typer.Typer(no_args_is_help=False, add_completion=False)
console = Console()
CONFIG_PATH = Path.home() / ".mouse-recorder" / "config.json"
DEFAULT_HOTKEYS = {"record_key": "key:f8", "play_key": "key:f9"}


def key_id(key: object) -> str:
    """Convert a pynput key into a small JSON-safe identifier."""
    char = getattr(key, "char", None)
    if char:
        return f"char:{char}"
    name = getattr(key, "name", None)
    if name:
        return f"key:{name}"
    return f"key:{key}"


def key_label(identifier: str) -> str:
    label = identifier.removeprefix("char:").removeprefix("key:")
    special_labels = {
        "esc": "ESC",
        "space": "SPACE",
        "enter": "ENTER",
        "tab": "TAB",
        "backspace": "BACKSPACE",
        "up": "UP",
        "down": "DOWN",
        "left": "LEFT",
        "right": "RIGHT",
    }
    return special_labels.get(label, label.upper() if label.startswith("f") else label)


def load_hotkeys() -> dict[str, str] | None:
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        record_key = str(data["record_key"])
        play_key = str(data["play_key"])
        if record_key == play_key:
            return None
        return {"record_key": record_key, "play_key": play_key}
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return DEFAULT_HOTKEYS.copy()


def capture_key(prompt: str) -> str:
    from pynput import keyboard

    console.print(prompt)
    captured: list[str] = []

    def on_press(key: object) -> bool:
        captured.append(key_id(key))
        return False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()
    return captured[0]


def setup_hotkeys() -> dict[str, str]:
    try:
        from pynput import keyboard  # noqa: F401
    except ImportError as exc:
        raise typer.ClickException("pynput is required for hotkey setup") from exc

    console.print("[bold]Mouse Recorder hotkey setup[/bold]")
    record_key = capture_key("Press the key you want to use for start / stop recording...")
    while True:
        play_key = capture_key("Press the key you want to use for start playback...")
        if play_key != record_key:
            break
        console.print("[yellow]The two hotkeys must be different. Please choose the playback key again.[/yellow]")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps({"record_key": record_key, "play_key": play_key}, indent=2) + "\n",
        encoding="utf-8",
    )
    console.print(
        f"[green]Hotkeys configured: Record {key_label(record_key)}, "
        f"Play latest {key_label(play_key)}[/green]"
    )
    return {"record_key": record_key, "play_key": play_key}


def interactive() -> None:
    """Keep a terminal session open and respond to global hotkeys."""
    try:
        from pynput import keyboard
    except ImportError as exc:
        raise typer.ClickException("pynput is required for interactive mode") from exc

    recordings = store()
    hotkeys = load_hotkeys() or DEFAULT_HOTKEYS.copy()
    state_lock = Lock()
    state: dict[str, object] = {"recording": None, "playing": None, "pending_play": False}

    def start_recording() -> None:
        with state_lock:
            recording_thread = state["recording"]
            if isinstance(recording_thread, Thread) and recording_thread.is_alive():
                console.print("[yellow]Stopping recording...[/yellow]")
                state["record_stop"].set()  # type: ignore[union-attr]
                return
            if state["playing"] is not None:
                console.print("[yellow]Playback is still running.[/yellow]")
                return
            stop_event = Event()
            state["record_stop"] = stop_event

            def run() -> None:
                try:
                    recording = Recorder(screen=screen_size()).record("latest", stop_event=stop_event)
                    path = recordings.save(recording)
                    console.print(f"[green]Saved latest recording:[/green] {path}")
                    console.print(f"Duration: {recording.duration:.1f}s | Events: {len(recording.events)}")
                except Exception as exc:
                    console.print(f"[red]Recording failed:[/red] {exc}")
                finally:
                    with state_lock:
                        state["recording"] = None

            thread = Thread(target=run, daemon=True)
            state["recording"] = thread
            thread.start()
            console.print(
                f"[bold red]Recording started[/bold red] "
                f"(press [{key_label(hotkeys['record_key'])}] to stop)"
            )

    def start_playback() -> None:
        with state_lock:
            recording_thread = state["recording"]
            if isinstance(recording_thread, Thread) and recording_thread.is_alive():
                if state["pending_play"]:
                    return
                state["pending_play"] = True
                stop_event = state.get("record_stop")
                if isinstance(stop_event, Event):
                    stop_event.set()
                console.print("[yellow]Stopping recording, then playing latest...[/yellow]")

                def play_after_recording() -> None:
                    recording_thread.join()
                    with state_lock:
                        state["pending_play"] = False
                    start_playback()

                Thread(target=play_after_recording, daemon=True).start()
                return
            if state["recording"] is not None:
                console.print("[yellow]Finishing recording...[/yellow]")
                return
            if state["playing"] is not None:
                abort_event = state.get("abort")
                if isinstance(abort_event, Event):
                    abort_event.set()
                    console.print("[yellow]Stopping playback...[/yellow]")
                return
            try:
                recording = recordings.load("latest")
            except (FileNotFoundError, ValueError):
                console.print("[yellow]No latest recording found.[/yellow]")
                return
            abort_event = Event()

            def run() -> None:
                try:
                    console.print("[cyan]Looping latest recording[/cyan] (press playback key or ESC to stop)")
                    Player(abort_event=abort_event, listen_for_abort=False).play(
                        recording, delay=0, loop=True
                    )
                    console.print("[green]Playback finished[/green]")
                except Exception as exc:
                    console.print(f"[red]Playback failed:[/red] {exc}")
                finally:
                    with state_lock:
                        state["playing"] = None

            thread = Thread(target=run, daemon=True)
            state["playing"] = thread
            state["abort"] = abort_event
            thread.start()

    def on_press(key: object) -> bool | None:
        identifier = key_id(key)
        if identifier == hotkeys["record_key"]:
            start_recording()
        elif identifier == hotkeys["play_key"]:
            start_playback()
        elif key == keyboard.Key.esc:
            with state_lock:
                abort_event = state.get("abort")
                if isinstance(abort_event, Event):
                    abort_event.set()
                    console.print("[yellow]Stopping playback...[/yellow]")
        return None

    console.print("[bold]Mouse Recorder[/bold] is ready")
    console.print(
        f"[{key_label(hotkeys['record_key'])}] start / stop recording   "
        f"[{key_label(hotkeys['play_key'])}] start playback   "
        "[ESC] stop playback   [Ctrl+C] exit"
    )
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    try:
        listener.join()
    except KeyboardInterrupt:
        listener.stop()
        console.print("\nBye")


def store() -> RecordingStore:
    return RecordingStore()


@app.command()
def record(name: str) -> None:
    try:
        typer.echo(f"Recording: {name}\n\nPress ESC to stop.")
        recording = Recorder(screen=screen_size()).record(name)
        path = store().save(recording)
        console.print(f"\nSaved recording: {name}")
        console.print(f"Duration: {recording.duration:.1f}s")
        console.print(f"Events: {len(recording.events)}")
        console.print(f"File: {path}")
    except (ValueError, RuntimeError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command()
def play(
    name: str,
    speed: float = typer.Option(1.0),
    repeat: int = typer.Option(1),
    delay: float = typer.Option(3.0),
    loop: bool = typer.Option(False, "--loop", help="Repeat forever until ESC is pressed."),
) -> None:
    if speed <= 0:
        raise typer.BadParameter("must be greater than 0", param_hint="--speed")
    if repeat < 1:
        raise typer.BadParameter("must be at least 1", param_hint="--repeat")
    if delay < 0:
        raise typer.BadParameter("must not be negative", param_hint="--delay")
    try:
        recording = store().load(name)
    except FileNotFoundError:
        typer.echo(f'Recording "{name}" was not found.', err=True)
        raise typer.Exit(1)
    except ValueError:
        typer.echo(f'Recording "{name}" is corrupted or invalid.', err=True)
        raise typer.Exit(1)
    current = screen_size()
    if recording.screen and current and recording.screen != current:
        console.print("[yellow]Warning: display configuration differs.[/yellow]")
        console.print(f"Recorded: {recording.screen['width']} x {recording.screen['height']}")
        console.print(f"Current:  {current['width']} x {current['height']}")
    mode = "Looping" if loop else "Playing"
    console.print(f"{mode}: {name}\n\nStarting in {delay:g} seconds...\n\nPress ESC to abort.")
    Player().play(recording, speed=speed, repeat=repeat, delay=delay, loop=loop)


@app.command(name="list")
def list_recordings() -> None:
    table = Table("NAME", "DURATION", "EVENTS", "CREATED")
    for name in store().list():
        try:
            recording = store().load(name)
        except ValueError:
            continue
        table.add_row(name, f"{recording.duration:.1f}s", str(len(recording.events)), recording.created_at[:10])
    console.print(table)


@app.command()
def info(name: str) -> None:
    try:
        recording = store().load(name)
    except FileNotFoundError:
        typer.echo(f'Recording "{name}" was not found.', err=True)
        raise typer.Exit(1)
    except ValueError:
        typer.echo(f'Recording "{name}" is corrupted or invalid.', err=True)
        raise typer.Exit(1)
    path = store().path_for(name)
    screen = recording.screen or {}
    console.print(f"Name: {recording.name}")
    console.print(f"Version: {recording.version}")
    console.print(f"Duration: {recording.duration:.3f} seconds")
    console.print(f"Events: {len(recording.events)}")
    console.print(f"Created at: {recording.created_at}")
    console.print(f"Recorded screen: {screen.get('width', 'unknown')} x {screen.get('height', 'unknown')}")
    console.print(f"File: {path}")


@app.command()
def delete(name: str, force: bool = typer.Option(False, "--force", "-f")) -> None:
    target = store().path_for(name)
    if not target.exists():
        typer.echo(f'Recording "{name}" was not found.', err=True)
        raise typer.Exit(1)
    if not force and not typer.confirm(f'Delete recording "{name}"?'):
        raise typer.Abort()
    store().delete(name)
    console.print(f'Deleted recording: {name}')


@app.command()
def doctor() -> None:
    console.print("\n".join(run_diagnostics()))


@app.command()
def setup() -> None:
    """Choose the hotkeys used by persistent terminal mode."""
    setup_hotkeys()


@app.callback(invoke_without_command=True)
def cli(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        interactive()


def main() -> None:
    app()

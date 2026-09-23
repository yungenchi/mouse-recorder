# Mouse Recorder

A lightweight command-line mouse macro recorder written in Python.

Mouse Recorder can record mouse movements, clicks, and scrolling, then replay them later with approximately the same timing.

The project is designed primarily for macOS, but the core functionality should also work on Windows and Linux where `pynput` is supported.

## Features

- Record mouse movement
- Record left, right, and middle mouse clicks
- Record mouse wheel scrolling
- Preserve timing between mouse events
- Replay recorded mouse actions
- Adjustable playback speed
- Repeat playback multiple times
- Configurable playback delay
- Emergency playback stop
- JSON-based recording files
- Simple command-line interface
- macOS permission diagnostics

## Requirements

- Python 3.11 or newer
- macOS, Windows, or Linux

Python 3.12+ is recommended.

## Installation

### Easiest: download the standalone macOS executable

For normal use, download the latest release from the project's GitHub
**Releases** page. Choose the file matching your Mac:

- `mouse-recorder-macos-arm64.zip` for Apple Silicon Macs (M1, M2, M3, and newer)
- `mouse-recorder-macos-x86_64.zip` for Intel Macs

Then:

1. Download and unzip the file.
2. Open Terminal and change to the unzipped folder.
3. Start it with `./mouse-recorder-macos-arm64` or
  `./mouse-recorder-macos-x86_64`.

The first time macOS blocks the executable, open **System Settings → Privacy &
Security** and allow it. Mouse control still requires **Accessibility** and
possibly **Input Monitoring** permission for the executable.

This download does not require Python, uv, pipx, or a virtual environment.

### Recommended: install as a command-line tool

Mouse Recorder is a command-line tool, so `pipx` or `uv tool` is recommended.
They install Mouse Recorder in its own environment and make the
`mouse-recorder` command available in your terminal.

#### Using pipx

After Mouse Recorder is published on PyPI:

Install `pipx` first if needed:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Restart your terminal, then install Mouse Recorder:

```bash
pipx install mouse-recorder
```

#### Using uv

After Mouse Recorder is published on PyPI:

```bash
uv tool install mouse-recorder
```

After installation, verify it:

```bash
mouse-recorder doctor
```

Start the persistent terminal mode:

```bash
mouse-recorder
```

### Install a downloaded package

When a release provides a wheel file such as
`mouse_recorder-0.1.0-py3-none-any.whl`, download it from the project's
Release page and install it with either:

```bash
pipx install ./mouse_recorder-0.1.0-py3-none-any.whl
```

or:

```bash
uv tool install ./mouse_recorder-0.1.0-py3-none-any.whl
```

The source archive (`.tar.gz`) is intended for package builders. Most users
should download the `.whl` file instead.

To build and install the current project locally:

```bash
uv build
uv tool install ./dist/mouse_recorder-0.1.0-py3-none-any.whl
```

The built files are written to the `dist/` directory.

For a GitHub release, upload the wheel from `dist/` as a release asset. The
`dist/` directory itself is intentionally ignored by Git and should not be
committed to the source repository.

### Developer installation

Use this option when you want to modify the source code.

#### 1. Clone or create the project

If you are creating the project manually:

```bash
mkdir mouse-recorder
cd mouse-recorder
```

Create the project structure described below and add the provided files.

If the project is stored in Git:

```bash
git clone <repository-url>
cd mouse-recorder
```

#### 2. Check your Python version

```bash
python3 --version
```

You should see Python 3.11 or newer.

Example:

```text
Python 3.12.7
```

#### 3. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, your terminal should look similar to:

```text
(.venv) user@computer mouse-recorder %
```

#### 4. Install the project in editable mode

From the project root:

```bash
pip install -e .
```

The `-e` flag installs the project in editable mode.

This means changes made to the Python source files will immediately be reflected when running the CLI.

#### 5. Verify the installation

Run:

```bash
mouse-recorder --help
```

You should see the available commands.

You can also run:

```bash
python -m mouse_recorder --help
```

## macOS Permissions

macOS requires Accessibility permission before an application can control the mouse.

Open:

```text
System Settings
→ Privacy & Security
→ Accessibility
```

Enable permission for the application that is running Mouse Recorder.

Depending on how you launch the program, this may be:

- Terminal
- iTerm
- Visual Studio Code
- PyCharm
- another terminal or IDE

You may also need permission under:

```text
System Settings
→ Privacy & Security
→ Input Monitoring
```

After changing permissions, restart the terminal or IDE before trying again.

You can check the environment using:

```bash
mouse-recorder doctor
```

## Usage

### Persistent terminal mode

For the simplest workflow, start Mouse Recorder without a command:

```bash
mouse-recorder
```

The default hotkeys are `F8` for recording and `F9` for playback. The terminal
shows the active button names when it starts.

To change them, run setup and press the two keys you want to use:

```bash
mouse-recorder setup
```

The choices are saved locally and reused next time.

Keep this terminal open and use the global hotkeys:

```text
your key  Start / stop recording
your key  Start playback
ESC      Stop playback
Ctrl+C   Exit Mouse Recorder
```

In persistent mode, press the playback key again or `ESC` to stop an infinite loop.

If you press the playback key while recording is still active, Mouse Recorder
automatically stops and saves the recording first, then starts playing it.

For an explicit command-line loop:

```bash
mouse-recorder play demo --loop
```

Recordings from this mode are saved as `latest.json`. The named commands below
remain available for managing recordings explicitly.

### Explicit command mode

The persistent terminal mode above is the recommended workflow. The following
commands are an optional way to record and manage a named recording directly
from the command line.

```bash
mouse-recorder record demo
```

While recording:

```text
Recording: demo

Press ESC to stop recording.
```

Mouse Recorder captures:

- mouse movement
- left click
- right click
- middle click
- scrolling
- event timing

When recording stops, the recording is saved automatically.

### List recordings

```bash
mouse-recorder list
```

Example:

```text
NAME       DURATION    EVENTS
demo       12.4s       428
login      5.8s        183
```

### Show recording information

```bash
mouse-recorder info demo
```

Example:

```text
Name:       demo
Duration:   12.4 seconds
Events:     428
Resolution: 2560 x 1440
```

### Play a recording

```bash
mouse-recorder play demo
```

By default, playback waits a few seconds before starting so you have time to switch to the correct application.

Example:

```text
Playing: demo

Starting in 3 seconds...

Press ESC to abort playback.
```

### Change playback speed

Play at double speed:

```bash
mouse-recorder play demo --speed 2
```

Play at half speed:

```bash
mouse-recorder play demo --speed 0.5
```

### Repeat playback

```bash
mouse-recorder play demo --repeat 5
```

This plays the recording five times.

Speed and repeat can be combined:

```bash
mouse-recorder play demo --speed 2 --repeat 5
```

### Change the startup delay

```bash
mouse-recorder play demo --delay 5
```

This gives you five seconds before playback starts.

### Delete a recording

```bash
mouse-recorder delete demo
```

## Emergency Stop

During playback, press:

```text
ESC
```

to stop immediately.

Playback should always be designed so the emergency-stop listener operates independently from the recorded mouse events.

The player also releases any mouse buttons during cleanup to reduce the chance of leaving a button in a pressed state after interruption.

## Recording Storage

Recordings are stored outside of the project directory.

Default location:

```text
~/.mouse-recorder/recordings/
```

Example:

```text
~/.mouse-recorder/
└── recordings/
    ├── demo.json
    └── login.json
```

A recording is stored as JSON.

Example:

```json
{
  "version": 1,
  "name": "demo",
  "screen": {
    "width": 2560,
    "height": 1440
  },
  "duration": 3.542,
  "events": [
    {
      "t": 0.0,
      "type": "move",
      "x": 842,
      "y": 412
    },
    {
      "t": 0.412,
      "type": "button",
      "button": "left",
      "pressed": true,
      "x": 901,
      "y": 430
    },
    {
      "t": 0.503,
      "type": "button",
      "button": "left",
      "pressed": false,
      "x": 901,
      "y": 430
    }
  ]
}
```

Because recordings use JSON, they can also be inspected or edited manually.

## Screen Resolution

Mouse Recorder uses absolute screen coordinates.

For example:

```text
x = 1200
y = 700
```

Because of this, playback works best when the screen configuration matches the configuration used during recording.

The recording stores information about the screen resolution.

If the current resolution differs from the recorded resolution, Mouse Recorder should display a warning before playback.

This is particularly important when using:

- multiple monitors
- different display scaling
- external monitors
- different resolutions
- different monitor arrangements

## Mouse Movement Sampling

Raw mouse movement can generate a very large number of events.

Mouse Recorder therefore throttles movement events instead of saving every tiny movement.

The target recording rate is approximately:

```text
100 Hz
```

or one movement sample every:

```text
10 ms
```

Clicks and scroll events are never intentionally discarded by movement throttling.

## CLI Commands

The initial CLI contains:

```bash
mouse-recorder record NAME
mouse-recorder play NAME
mouse-recorder list
mouse-recorder info NAME
mouse-recorder delete NAME
mouse-recorder doctor
```

Run:

```bash
mouse-recorder --help
```

for the complete command list.

For help with a specific command:

```bash
mouse-recorder play --help
```

## Project Structure

```text
mouse-recorder/
├── README.md
├── pyproject.toml
├── .gitignore
│
├── src/
│   └── mouse_recorder/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── models.py
│       ├── storage.py
│       ├── recorder.py
│       ├── player.py
│       └── doctor.py
│
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_storage.py
    └── test_player.py
```

### `cli.py`

Defines the command-line interface.

Responsibilities:

- `record`
- `play`
- `list`
- `info`
- `delete`
- `doctor`
- command arguments and options
- user-facing terminal output

### `models.py`

Defines the internal recording data structures.

Responsibilities:

- mouse event models
- recording metadata
- JSON serialization
- JSON deserialization

### `storage.py`

Handles recording files.

Responsibilities:

- recording directory creation
- save recordings
- load recordings
- list recordings
- delete recordings

### `recorder.py`

Handles mouse recording.

Responsibilities:

- mouse listeners
- mouse movement
- mouse buttons
- scrolling
- timestamps
- movement throttling
- recording stop handling

### `player.py`

Handles playback.

Responsibilities:

- event timing
- mouse movement
- mouse clicks
- scrolling
- playback speed
- repeat
- emergency stop
- cleanup

### `doctor.py`

Checks whether the current system appears ready to record and replay mouse actions.

Responsibilities:

- operating system information
- screen information
- recording directory
- mouse-control checks
- macOS permission hints

### `__main__.py`

Allows the application to run with:

```bash
python -m mouse_recorder
```

### `tests/`

Contains automated tests for functionality that does not require physically moving the user's mouse.

## Development

Install the project in editable mode:

```bash
pip install -e .
```

Run the CLI:

```bash
mouse-recorder --help
```

Run the tests:

```bash
pytest
```

The `tests/` directory is part of the source repository and should be kept on
GitHub. It is not included in the installed wheel. Build outputs, virtual
environments, caches, local recordings, and local configuration are excluded
by `.gitignore`.

## Design Principles

The first version intentionally remains small.

Mouse Recorder is not intended to be a complete desktop automation framework.

Version 0.1 focuses on:

```text
record
→ save
→ inspect
→ replay
```

Features such as keyboard recording, image recognition, application detection, conditional logic, and graphical macro editing are intentionally outside the initial scope.

## Safety

Mouse automation can interact with applications very quickly.

Before replaying a recording:

1. Make sure the expected application is open.
2. Make sure the screen layout matches the recording.
3. Keep the emergency-stop key available.
4. Test new recordings with a single playback before using repeat mode.
5. Avoid replaying macros blindly on destructive or sensitive interfaces.

## License

Choose a license before publishing the project publicly.

For a small open-source utility, the MIT License is a common option.
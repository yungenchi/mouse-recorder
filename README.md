# Mouse Recorder

Mouse Recorder records your mouse movements, clicks, and scrolling so you can
play the same actions again later. It is useful for repeating simple mouse
workflows on macOS.

## Download

Mouse Recorder currently supports Apple Silicon Macs (M1, M2, M3, and newer).
The easiest way to install it is with Homebrew:

```bash
brew install --cask yungenchi/mouse-recorder/mouse-recorder
```

If your Mac says `brew: command not found`, install Homebrew first from
[brew.sh](https://brew.sh), then run the command above again.

You can also download the latest release from the
[GitHub Releases page](https://github.com/yungenchi/mouse-recorder/releases).
The Homebrew install is recommended for most people.

## First-time setup

macOS must allow Mouse Recorder to control the mouse and listen for keyboard
shortcuts. After installing, run:

```bash
mouse-recorder doctor
```

This checks your permissions and opens the required macOS settings pages when
something is missing.

### If macOS blocks the first launch

You may see a message saying that macOS cannot verify Mouse Recorder. Choose
**Done** (do not move it to the Trash), then open **System Settings > Privacy &
Security**. Scroll down and choose **Open Anyway** for Mouse Recorder. You may
need to enter your Mac password.

In **System Settings > Privacy & Security**, enable Mouse Recorder in:

- **Accessibility**
- **Input Monitoring**

After enabling both permissions, run the check again:

```bash
mouse-recorder doctor
```

When both permissions show `OK`, Mouse Recorder is ready to use. If macOS asks
you to add the application manually, add Mouse Recorder and enable its switch.

## Use Mouse Recorder

Start the app:

```bash
mouse-recorder
```

When the terminal shows that Mouse Recorder is ready, switch to the app where
you want to repeat a task.

Use the default global hotkeys:

- `F8`: start or stop recording
- `F9`: play the latest recording
- `ESC`: stop playback
- `Ctrl+C`: quit Mouse Recorder

Move and click the mouse while recording. Press `F8` again to stop. The latest
recording is saved automatically. Press `F9` to play it back.

The first playback starts after a short delay so you can switch to the target
application. Playback repeats until you stop it with `F9` or `ESC`.

> **Safety tip:** For your first playback, record a simple harmless action and
> test it once. Keep `ESC` available so you can stop playback immediately.

On many Mac laptops, you may need to hold `fn` while pressing `F8` or `F9`.
You can also change the hotkeys with `mouse-recorder setup`.

## Optional commands

Save and play recordings with a name instead of using the latest recording:

```bash
mouse-recorder record demo
mouse-recorder play demo
```

Useful options:

```bash
mouse-recorder play demo --speed 2
mouse-recorder play demo --repeat 5
mouse-recorder list
```

Run `mouse-recorder --help` to see all commands.

## Change the hotkeys

To choose different keys for recording and playback, run:

```bash
mouse-recorder setup
```

Follow the prompts, then use the new keys the next time you start
Mouse Recorder.

## Notes

- Playback works best with the same display arrangement and resolution used
  during recording.
- Recordings are stored in `~/.mouse-recorder/recordings/`.
- To update or remove the app:

```bash
brew upgrade --cask mouse-recorder
brew uninstall --cask mouse-recorder
```

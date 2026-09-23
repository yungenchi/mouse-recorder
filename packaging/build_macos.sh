#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON_BIN=${PYTHON_BIN:-python3.12}
VERSION=$(sed -n 's/^version = "\([^"]*\)"/\1/p' "$ROOT_DIR/pyproject.toml" | head -n 1)
ARCH=$(uname -m)
VENV_DIR="$ROOT_DIR/.build-venv"
RELEASE_DIR="$ROOT_DIR/release"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    printf 'Missing %s. Install Python 3.12+ or set PYTHON_BIN.\n' "$PYTHON_BIN" >&2
    exit 1
fi

if [ "$ARCH" != "arm64" ]; then
    printf 'This release currently supports Apple Silicon (arm64) only.\n' >&2
    printf 'Detected architecture: %s\n' "$ARCH" >&2
    exit 1
fi

"$PYTHON_BIN" -c 'import sys; sys.exit("Python 3.11+ is required") if sys.version_info < (3, 11) else None'
"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install . pyinstaller

rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist"
"$VENV_DIR/bin/pyinstaller" \
    --clean \
    --onefile \
    --name mouse-recorder \
    --console \
    --paths "$ROOT_DIR/src" \
    "$ROOT_DIR/packaging/macos_entrypoint.py"

mkdir -p "$RELEASE_DIR"
BINARY_NAME="mouse-recorder-macos-$ARCH"
cp "$ROOT_DIR/dist/mouse-recorder" "$RELEASE_DIR/$BINARY_NAME"
chmod +x "$RELEASE_DIR/$BINARY_NAME"
(cd "$RELEASE_DIR" && zip -q -FS "$BINARY_NAME.zip" "$BINARY_NAME")
(cd "$RELEASE_DIR" && shasum -a 256 "$BINARY_NAME.zip" > SHA256SUMS)

printf '\nBuilt Mouse Recorder %s for %s:\n' "$VERSION" "$ARCH"
printf '  %s\n' "$RELEASE_DIR/$BINARY_NAME.zip"
printf '  %s\n' "$RELEASE_DIR/SHA256SUMS"
printf '\nCreate the GitHub release with:\n'
printf '  gh release create v%s %s/*.zip %s/SHA256SUMS --title v%s --generate-notes\n' "$VERSION" "$RELEASE_DIR" "$RELEASE_DIR" "$VERSION"

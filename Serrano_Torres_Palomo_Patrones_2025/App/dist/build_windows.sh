#!/usr/bin/env bash
set -euo pipefail

# Helper script for Windows build. Building a native Windows .exe on Linux is non-trivial.
# Recommended options:
#  - Run this script on Windows (Git Bash / PowerShell) with Python installed.
#  - Or use the provided GitHub Actions workflow (recommended) to produce Windows artifacts.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# If we detect a Windows environment, run pyinstaller with Windows separators
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*|Windows_NT)
    echo "Detected Windows-like environment. Running pyinstaller for Windows."
    python -m venv .venv_build
    source .venv_build/Scripts/activate
    pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt || true
    fi
    pip install pyinstaller
    PYINSTALLER_NAME="GameApp"
    # On Windows the add-data separator is ';' and use absolute path for source assets
    pyinstaller --noconfirm --onefile \
      --name "$PYINSTALLER_NAME" \
      --add-data "$ROOT_DIR/Assets;Assets" \
      --paths src \
      --distpath dist/windows \
      --workpath build \
      --specpath build \
      src/main.py
    echo "Windows build finished. Binary in dist/windows/$PYINSTALLER_NAME.exe"
    ;;
  *)
    echo "Not running on Windows. To produce a Windows exe, either run this on Windows or use the GitHub Actions workflow included in the README (recommended)."
    exit 1
    ;;
esac
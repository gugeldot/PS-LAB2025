#!/usr/bin/env bash
set -euo pipefail

# Simple build script to create a single-file Linux executable using PyInstaller.
# Run this from the App/ directory: ./dist/build_linux.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# 1) create venv
python3 -m venv .venv_build
source .venv_build/bin/activate

# 2) upgrade pip and install requirements (+ pyinstaller)
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || true
fi
pip install pyinstaller

# 3) Run pyinstaller. We include the src path so imports from src/ work.
# Adjust --add-data entries if you need to bundle more assets. On Linux the separator is ':'
PYINSTALLER_NAME="GameApp"
pyinstaller --noconfirm --onefile \
  --name "$PYINSTALLER_NAME" \
  --add-data "$ROOT_DIR/Assets:Assets" \
  --paths src \
  --distpath dist/linux \
  --workpath build \
  --specpath build \
  src/main.py

echo "Linux build finished. Binary is in dist/linux/$PYINSTALLER_NAME"

echo "Note: if your app expects assets relative to cwd, run the binary from the project root or adapt runtime asset paths."
#!/usr/bin/env bash
set -e
echo "Building FishScript macOS app..."
python -m pip install pyinstaller
pyinstaller --name FishScript --windowed --onefile fishscript/ide.py
echo "Done. Check the dist folder."

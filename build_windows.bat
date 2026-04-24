@echo off
echo Building FishScript Windows app...
pip install pyinstaller
pyinstaller --name FishScript --windowed --onefile fishscript/ide.py
echo Done. Check the dist folder.
pause

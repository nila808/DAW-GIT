#!/bin/bash

# Go to project directory (same folder as build.sh)
cd "$(dirname "$0")"

# Clean previous builds
rm -rf build/ dist/ daw_git_gui.spec

# Build the app
pyinstaller --noconfirm --windowed --name "DAW Git" --icon=icon.icns \
--add-data "icon.png:." \
--hidden-import PyQt6 \
--hidden-import PyQt6.QtWidgets \
--hidden-import PyQt6.QtGui \
--hidden-import PyQt6.QtCore \
--hidden-import git \
daw_git_gui.py


# ✅ After building, manually copy styles/ into app
echo "Copying styles/ into the .app bundle..."
cp -R styles dist/DAW\ Git.app/Contents/MacOS/

echo "✅ Build complete!"

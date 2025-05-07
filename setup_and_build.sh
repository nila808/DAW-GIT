#!/bin/bash

# Go to project folder
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "daw-git-env" ]; then
  echo "⚡ Virtual environment not found. Creating daw-git-env..."
  python3 -m venv daw-git-env
fi

# Activate virtual environment
source daw-git-env/bin/activate

# Install pyinstaller if not installed
if ! pip show pyinstaller > /dev/null 2>&1; then
  echo "⚡ PyInstaller not found. Installing..."
  pip install pyinstaller
fi

# Install PyQt6 and GitPython if missing
if ! pip show pyqt6 > /dev/null 2>&1; then
  echo "⚡ PyQt6 not found. Installing..."
  pip install pyqt6
fi

if ! pip show gitpython > /dev/null 2>&1; then
  echo "⚡ GitPython not found. Installing..."
  pip install gitpython
fi

# Clean previous builds
echo "🧹 Cleaning old builds..."
rm -rf build/ dist/ daw_git_gui.spec

# Build app
echo "🚀 Building app..."
if pyinstaller --noconfirm --windowed --name "DAW Git" --icon=icon.icns \
--add-data "icon.png:." \
--hidden-import PyQt6 --hidden-import PyQt6.QtWidgets --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtCore \
--hidden-import git \
--target-architecture x86_64 \
--osx-bundle-identifier com.example.dawgit \
daw_git_gui.py; then

    echo "✅ Build succeeded."

    # Copy styles manually into the correct place inside Contents/MacOS/
    echo "✅ Copying styles folder..."
    cp -R styles dist/DAW\ Git.app/Contents/MacOS/

    # Launch app automatically
    echo "🚀 Launching app..."
    open "dist/DAW Git.app"

else
    echo "❌ Build failed. No styles copied. App not launched."
fi

echo "🎉 All done!"
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

#!/bin/bash

echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/ DAW\ Git.spec

echo "🚀 Building the DAW Git app..."
pyinstaller \
  --noconfirm \
  --windowed \
  --name "DAW Git" \
  --icon=icon.icns \
  --add-data "styles:styles" \
  --add-data "icon.png:." \
  daw_git_gui.py

echo "✅ Build complete!"

# --- Copy styles manually into app bundle if needed ---
echo "📂 Copying styles folder into the app..."
cp -R styles/ "dist/DAW Git.app/Contents/MacOS/styles/"

echo "✅ Styles copied!"

# --- Optional: Auto-launch app after build ---
echo "🚀 Launching the app..."
open "dist/DAW Git.app"

echo "🎉 Build and launch complete!"

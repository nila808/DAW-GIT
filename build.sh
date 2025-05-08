#!/bin/bash

APP_NAME="DAW Git"
APP_BUNDLE="dist/$APP_NAME.app"

echo "🧹 Cleaning old build files..."
rm -rf build/ dist/ __pycache__/ "$APP_NAME.spec"

echo "🚀 Building binary with PyInstaller..."
pyinstaller \
    --noconfirm \
    --onedir \
    --windowed \
    --name "$APP_NAME" \
    --icon=icon.icns \
    --add-data "styles:styles" \
    --add-data "icon.png:." \
    daw_git_gui.py

echo "📦 Creating proper macOS .app bundle..."

# Create .app folder structure manually
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Move built binary into MacOS
mv "dist/$APP_NAME/$APP_NAME" "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

# Move styles and icon into Resources
cp -R styles "$APP_BUNDLE/Contents/Resources/"
cp icon.png "$APP_BUNDLE/Contents/Resources/"
cp icon.icns "$APP_BUNDLE/Contents/Resources/"

# Create minimal Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" <<EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.niccavendish.dawgit</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
</dict>
</plist>
EOL

echo "✅ App bundle created: $APP_BUNDLE"

# (Optional) Open dist/ folder
open dist/

echo "🎉 Done! You can now double-click your app!"

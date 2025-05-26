#!/bin/bash
set -e

VERSION="$1"
MESSAGE="$2"

# --- Validate input ---
if [[ -z "$VERSION" ]]; then
  echo "❌ Usage: push-it <version-tag> \"optional commit message\""
  exit 1
fi

# Ensure tag is alphanumeric with dashes or underscores only
if ! [[ "$VERSION" =~ ^[a-zA-Z0-9._-]+$ ]]; then
  echo "❌ Invalid tag: $VERSION"
  echo "Tags can only contain letters, numbers, dots, dashes, or underscores."
  exit 1
fi

# Default commit message
if [[ -z "$MESSAGE" ]]; then
  MESSAGE="📦 $VERSION: 🔖 automated release commit"
fi

echo "🧪 Running test suite..."
pytest -q > /dev/null || {
  echo "❌ Tests failed — aborting release."
  exit 1
}
echo "✅ All tests passed."

echo "🔧 Updating PROJECT_STATUS.md..."
if [[ -f PROJECT_STATUS.md ]]; then
  sed -i '' "s/^Current Version:.*/Current Version: $VERSION/" PROJECT_STATUS.md
else
  echo "Current Version: $VERSION" > PROJECT_STATUS.md
fi

echo "📝 Updating CHANGELOG.md..."
echo "- $VERSION ($(date +%Y-%m-%d)): $MESSAGE" >> CHANGELOG.md

echo "📁 Updating PROJECT_MARKER.json..."
if [[ -f PROJECT_MARKER.json ]]; then
  jq --arg ver "$VERSION" '.version = $ver' PROJECT_MARKER.json > tmp_marker && mv tmp_marker PROJECT_MARKER.json
else
  echo "{ \"version\": \"$VERSION\" }" > PROJECT_MARKER.json
fi

echo "📦 Staging all changes..."
git add -A

echo "📝 Committing..."
git commit -m "$MESSAGE"

echo "🚀 Pushing commit..."
git push

echo "🏷️ Tagging: $VERSION"
git tag "$VERSION"
git push origin "$VERSION"

echo "✅ Done — release $VERSION complete."

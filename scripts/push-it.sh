#!/bin/bash
set -e

# --- Always run from repo root ---
cd "$(git rev-parse --show-toplevel)"

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

# --- Check if tag already exists ---
if git rev-parse "$VERSION" >/dev/null 2>&1; then
  echo "❌ Tag '$VERSION' already exists. Use a new tag."
  exit 1
fi

# --- Safety check BEFORE staging ---
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️ Detected unstaged or uncommitted changes."
  echo "💡 Please run: git add ."
  echo "Or manually stage only what you want before running push-it."
  exit 1
fi

echo "✅ Working directory clean — proceeding with tests..."

# --- Run test suite ---
echo "🧪 Running test suite..."
export DAWGIT_TEST_MODE=1
export DAWGIT_FORCE_INPUT=1

pytest -v || {
  echo ""
  echo "❌ Tests failed — aborting release."
  echo "💡 Fix the issue, rerun tests, and retry with: push-it <tag> \"message\""
  exit 1
}
echo "✅ All tests passed."

# --- Stage and update metadata AFTER tests pass ---
echo "📦 Staging release updates..."
git add .

# --- Update project status ---
echo "🔧 Updating PROJECT_STATUS.md..."
if [[ -f PROJECT_STATUS.md ]]; then
  sed -i '' "s/^Current Version:.*/Current Version: $VERSION/" PROJECT_STATUS.md
else
  echo "Current Version: $VERSION" > PROJECT_STATUS.md
fi

# --- Update changelog ---
echo "📝 Updating CHANGELOG.md..."
echo "- $VERSION ($(date +%Y-%m-%d)): $MESSAGE" >> CHANGELOG.md

# --- Update marker file ---
echo "📁 Updating PROJECT_MARKER.json..."
if [[ -f PROJECT_MARKER.json ]]; then
  jq --arg ver "$VERSION" '.version = $ver' PROJECT_MARKER.json > tmp_marker && mv tmp_marker PROJECT_MARKER.json
else
  echo "{ \"version\": \"$VERSION\" }" > PROJECT_MARKER.json
fi

# --- Final commit + tag + push ---
git add -A

echo "📝 Committing..."
git commit -m "$MESSAGE"

echo "🚀 Pushing commit..."
git push

echo "🏷️ Tagging: $VERSION"
git tag "$VERSION"
git push origin "$VERSION"

echo "✅ Done — release $VERSION complete."

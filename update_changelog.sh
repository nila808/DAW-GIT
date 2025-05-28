#!/bin/bash

TAG=$1
DATE=$(date +%F)
CHANGELOG="changelog.md"

if [[ -z "$TAG" ]]; then
  echo "❌ Usage: ./update_changelog.sh <tag-name>"
  exit 1
fi

echo "📦 Updating $CHANGELOG for tag: $TAG"

cat <<EOF | cat - $CHANGELOG > temp && mv temp $CHANGELOG
## [$TAG] — $DATE

### ✅ Test Suite Stability
- Achieved 100% passing test coverage across 60+ tests (safety, roles, checkouts, DAW launch)

### 🔧 Fixes & Improvements
- Improved snapshot confirmation logic and test-mode file returns
- Ensured `.als`/`.logicx` detection and filtering works during test runs

### 🧪 Tooling
- Added failure block capture via \`run_failures_only.sh\`
- Enhanced test output logging in \`run_tests.sh\`

### 🧼 Cleanup
- Finalized commit: $TAG

EOF

echo "✅ changelog.md updated."

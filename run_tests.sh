#!/bin/bash

# 🔒 Guaranteed cleanup even if script is interrupted or fails
trap 'echo "🧹 Final cleanup..."; rm -rf ~/pytest-of-*; find /private/var/folders -type d -name "pytest-of-*" 2>/dev/null -exec rm -rf {} +' EXIT

echo "🧪 Running DAW Git App test suite..."
# Runs all tests
# pytest -v tests_dawgitc

# Runs individual tests
pytest "$@"

echo "🧹 Cleaning up test artifacts..."
python3 cleanup_temp_test_folders.py
bash cleanup_temp_test_folders.sh

if [ -f tests_dawgit/test_full_workflow.py ]; then
  echo "🔁 Running full end-to-end test..."
  pytest -v tests_dawgit/test_full_workflow.py
else
  echo "⚠️  End-to-end test file not found."
fi

echo "✅ All done."

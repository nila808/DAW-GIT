#!/bin/bash

echo "🧪 Running DAW Git App test suite..."
pytest -v tests_dawgit

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

echo "🧹 Cleaning up leftover pytest folders..."

# ✅ Clean up from user home (if any)
rm -rf ~/pytest-of-*

# ✅ Clean up from macOS temp system folders
find /private/var/folders -type d -name "pytest-of-*" -exec rm -rf {} +

echo "🧼 Temp pytest folders removed."

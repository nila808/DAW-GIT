#!/bin/bash

# 🔒 Guaranteed cleanup even if script is interrupted or fails
trap 'echo "🧹 Final cleanup..."; rm -rf ~/pytest-of-*; find /private/var/folders -type d -name "pytest-of-*" 2>/dev/null -exec rm -rf {} +' EXIT

echo "🧪 Running DAW Git App test suite..."

# ✅ Enable test mode to suppress launching Ableton
export DAWGIT_TEST_MODE=1


# ⏱️ Run tagging test with timeout to catch hangs
pytest tests_dawgit/test_commit_tagging.py -v -s --timeout=10 | tee -a test_output.log

# Runs all tests and logs output
# pytest --color=yes -s -v tests_dawgit/ | tee test_output.log
# Runs single tests and logs output
pytest "$@"

# ✂️ If failures are detected, copy from FAILURES to end
if grep -q "FAILURES" test_output.log; then
  awk '/=+ FAILURES =+/,0' test_output.log | pbcopy
  echo "📋 Copied failure block to clipboard."
else
  echo "✅ No failures to copy."
fi

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

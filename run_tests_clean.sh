#!/bin/bash

echo "🧹 Temporarily disabling DAWGIT_FORCE_TEST_PATH..."
ORIGINAL_DAWGIT_PATH="$DAWGIT_FORCE_TEST_PATH"
unset DAWGIT_FORCE_TEST_PATH

echo "🧪 Running DAW Git App tests in clean temp paths..."
./run_tests.sh

echo ""
echo "♻️ Restoring DAWGIT_FORCE_TEST_PATH..."
export DAWGIT_FORCE_TEST_PATH="$ORIGINAL_DAWGIT_PATH"

echo "✅ Done. Environment restored."

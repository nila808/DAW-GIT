#!/bin/bash

echo "🧹 Cleaning up temp folders older than 1 hour..."
tempdir=$(python3 -c "import tempfile; print(tempfile.gettempdir())")

find "$tempdir" -type d -name 'tmp*' -mmin +60 -exec rm -rf {} + 2>/dev/null
echo "✅ OS temp folder cleanup complete."

# 🔧 DAWGitApp-specific cleanup
echo "🧹 Cleaning up DAWGitApp project temp folders..."
rm -rf .dawgit_checkout_work/ .dawgit_cache/ .version_marker 2>/dev/null
echo "✅ Project folder cleanup complete."

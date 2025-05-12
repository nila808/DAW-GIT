#!/bin/bash

echo "🧹 Cleaning up temp folders older than 1 hour..."
tempdir=$(python3 -c "import tempfile; print(tempfile.gettempdir())")

find "$tempdir" -type d -name 'tmp*' -mmin +60 -exec rm -rf {} + 2>/dev/null

echo "✅ Temp folder cleanup complete."

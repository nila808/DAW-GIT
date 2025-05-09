#!/bin/bash
echo "🧪 Running DAWGitApp test suite..."
cd "$(dirname "$0")/tests_dawgit"
pytest -v

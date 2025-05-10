#!/bin/bash
echo "🧪 Running DAWGitApp test suite..."
export PYTHONPATH="$(pwd)"
pytest -v tests_dawgit

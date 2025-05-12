#!/bin/bash
echo "🧪 Running DAWGitApp test suite..."

# Ensure daw_git_gui.py is importable
export PYTHONPATH="$(pwd)"

pytest -v tests_dawgit

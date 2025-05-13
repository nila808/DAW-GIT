#!/bin/bash
echo "🧪 Running DAWGitApp test suite..."
PYTHONPATH=. pytest "$@"

# Set Python path to ensure daw_git_gui.py is importable
export PYTHONPATH=$(pwd)

# Activate virtual environment if needed
# source venv/bin/activate  # Uncomment if you're using a virtualenv

# Run tests
pytest -v tests_dawgit

# Run cleanup scripts after tests
echo "🧹 Cleaning up test artifacts..."
python3 cleanup_temp_test_folders.py
bash cleanup_temp_test_folders.sh

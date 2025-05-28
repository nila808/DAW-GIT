#!/bin/bash

# 💻 Activate virtual environment early
echo "💻 Activating virtual environment..."
source daw-git-env/bin/activate

# ✅ Leave test mode env intact if it was set externally
if [[ "$DAWGIT_TEST_MODE" == "1" ]]; then
  echo "🧽 Running ref cleaner..."
  python3 scripts/clean_git_refs.py
fi

echo "🧹 Cleaning up Python cache and test artifacts..."
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -exec rm -f {} +
rm -rf .pytest_cache

echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "🚀 Launching DAW Git GUI..."
python daw_git_gui.py

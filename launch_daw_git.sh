#!/bin/bash

echo "🧹 Cleaning up Python cache and test artifacts..."
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -exec rm -f {} +
rm -rf .pytest_cache

echo "💻 Activating virtual environment..."
source daw-git-env/bin/activate

echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "🚀 Launching DAW Git GUI..."
python daw_git_gui.py

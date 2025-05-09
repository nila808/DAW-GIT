#!/bin/bash

# Define virtual environment directory
VENV_DIR="daw-git-env"

# Step 1: Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Step 2: Activate environment
echo "💻 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Step 3: Install dependencies
echo "📦 Installing requirements..."
pip install --upgrade pip
pip install PyQt6 gitpython

# Step 4: Run the app
echo "🚀 Launching DAW Git GUI..."
python3 daw_git_gui.py

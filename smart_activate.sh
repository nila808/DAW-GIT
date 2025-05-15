#!/bin/bash

# Go to project root
cd "$(dirname "$0")"

# Check if inside a virtual environment already
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Already inside a virtual environment: $VIRTUAL_ENV"
    exit 0
fi

# Check if daw-git-env exists
if [ ! -d "daw-git-env" ]; then
    echo "⚡ No daw-git-env found. Creating it..."
    python3 -m venv daw-git-env
fi

# Activate depending on current folder
if [ -f "daw-git-env/bin/activate" ]; then
    echo "✅ Activating daw-git-env..."
    source daw-git-env/bin/activate
else
    echo "❌ Could not find daw-git-env/bin/activate!"
    exit 1
fi

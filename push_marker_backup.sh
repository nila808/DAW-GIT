#!/bin/bash

# Set paths
SRC_DIR="/mnt/data"
DEST_DIR="$HOME/Projects/DAWGitApp"
MARKER_FILE="PROJECT_MARKER.json"
TRACKER_FILE="test_tracker.json"

# Copy files
cp "$SRC_DIR/$MARKER_FILE" "$DEST_DIR/"
cp "$SRC_DIR/$TRACKER_FILE" "$DEST_DIR/"

# Change directory
cd "$DEST_DIR" || { echo "❌ Failed to find DAWGitApp directory."; exit 1; }

# Git add, commit, push
git add "$MARKER_FILE" "$TRACKER_FILE"
git commit -m "📌 Added test tracker and project marker for v1.0.2"
git push

echo "✅ Project marker and test tracker pushed successfully."

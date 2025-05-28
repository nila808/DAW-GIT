#!/bin/bash

CHANGELOG="$HOME/Projects/DAWGitApp/CHANGELOG.md"

echo "📝 What’s the changelog entry?"
read -r entry

timestamp=$(date +"%Y-%m-%d %H:%M")
echo "- [$timestamp] $entry" >> "$CHANGELOG"

echo "✅ Entry added to CHANGELOG.md"


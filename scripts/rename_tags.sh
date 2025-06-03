#!/bin/bash

echo "🚧 Backing up existing tags to backup/old_tag_name..."
mkdir -p .tag_backup

# Step 1: Create a list of all tags sorted by creation date
tags=($(git tag --sort=creatordate))

# Step 2: Loop through each tag and rename it to v0.0.X
counter=0
for old_tag in "${tags[@]}"; do
    new_tag="v0.0.$counter"

    # Get the commit the tag points to
    commit=$(git rev-list -n 1 "$old_tag")

    # Backup the tag
    echo "$commit $old_tag" >> .tag_backup/tag_backup_map.txt

    # Delete the old local tag
    git tag -d "$old_tag"

    # Create the new tag at the same commit
    git tag "$new_tag" "$commit"

    echo "🔁 Renamed $old_tag ➜ $new_tag"

    ((counter++))
done

echo "✅ Local tags renumbered sequentially as v0.0.X"
echo "📝 Backup saved to .tag_backup/tag_backup_map.txt"

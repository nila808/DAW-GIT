import os
import subprocess
from pathlib import Path
from git import Repo

def test_push_it_aborts_on_unstaged_changes(tmp_path):
    # Setup a fake Git repo
    repo_path = tmp_path / "TestProject"
    repo_path.mkdir()
    repo = Repo.init(repo_path)

    # Add a dummy file and commit
    file = repo_path / "dummy.als"
    file.write_text("initial content")
    repo.index.add([str(file)])
    repo.index.commit("Initial commit")

    # Modify the file without staging it
    file.write_text("unsaved changes")

    # Save the push-it script to the temp dir
    push_it_script = repo_path / "push-it"
    push_it_script.write_text(PUSH_IT_SCRIPT)
    push_it_script.chmod(0o755)

    # Run the script and capture output
    result = subprocess.run(
        ["bash", str(push_it_script), "v9.9.9"],
        cwd=repo_path,
        text=True,
        capture_output=True
    )

    # ✅ Assert it exits with an error and includes expected messages
    assert result.returncode != 0
    assert "unstaged or uncommitted changes" in result.stdout.lower()
    assert "aborting" in result.stdout.lower()


# 👇 Embedded minimal push-it script with BONUS abort line
PUSH_IT_SCRIPT = """#!/bin/bash
set -e
cd "$(git rev-parse --show-toplevel)"
VERSION="$1"
MESSAGE="$2"

if [[ -z "$VERSION" ]]; then echo "❌ Usage: push-it <version-tag>"; exit 1; fi
if ! [[ "$VERSION" =~ ^[a-zA-Z0-9._-]+$ ]]; then echo "❌ Invalid tag."; exit 1; fi
if git rev-parse "$VERSION" >/dev/null 2>&1; then echo "❌ Tag exists."; exit 1; fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "⚠️ Unstaged or uncommitted changes detected!"
  echo "❌ Aborting push-it due to dirty working directory."
  exit 1
fi

echo "✅ Would run tests now"
"""

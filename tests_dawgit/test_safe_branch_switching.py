import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from git import Repo
from daw_git_gui import DAWGitApp

def test_prevent_branch_switch_with_uncommitted_changes(tmp_path):
    project_file = tmp_path / "track.als"
    project_file.write_text("Initial version")
    repo = Repo.init(tmp_path)
    repo.index.add(["track.als"])
    repo.index.commit("Initial commit")

    # Simulate uncommitted change
    project_file.write_text("Uncommitted edit")

    app = DAWGitApp()
    app.repo_path = tmp_path
    app.repo = repo

    # Try to switch branch with uncommitted changes
    result = app.safe_switch_branch("new-branch")

    assert result["status"] == "warning"
    assert "uncommitted" in result["message"].lower()
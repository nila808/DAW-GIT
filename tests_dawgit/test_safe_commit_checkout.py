import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from git import Repo
from daw_git_gui import DAWGitApp

def test_untracked_file_warning_on_checkout(tmp_path):
    project_file = tmp_path / "track.als"
    project_file.write_text("Original")
    repo = Repo.init(tmp_path)
    repo.index.add(["track.als"])
    repo.index.commit("Initial commit")
    commit_hash = repo.head.commit.hexsha

    # Create untracked file
    untracked = tmp_path / "extra.wav"
    untracked.write_text("Untracked audio")

    app = DAWGitApp(project_path=tmp_path, build_ui=False)
    app.repo = repo

    # Attempt to checkout the commit hash
    result = app.checkout_selected_commit(commit_hash)

    assert result["status"] == "warning"
    assert "untracked" in result["message"].lower()

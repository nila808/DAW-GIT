import ui_strings
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from git import Repo
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QLabel


def test_untracked_file_warning_on_checkout(tmp_path):

    # Step 1: Init repo with valid .als file
    repo = Repo.init(tmp_path)
    als_file = tmp_path / "session.als"
    als_file.write_text("Session 1")
    repo.index.add(["session.als"])
    repo.index.commit("Initial version")

    # Step 2: Add 2nd commit with change
    als_file.write_text("Session 2")
    repo.index.add(["session.als"])
    repo.index.commit("Second version")

    # Step 3: Create an untracked file
    untracked = tmp_path / "notes.txt"
    untracked.write_text("Do not lose me")

    # Step 4: Launch app and try checkout
    app = DAWGitApp(project_path=tmp_path, build_ui=False)

    app.branch_label = QLabel()
    app.commit_label = QLabel()
    app.update_status_label = lambda: None
    app.init_git()

    old_commit_sha = list(repo.iter_commits("HEAD", max_count=2))[1].hexsha
    result = app.checkout_selected_commit(old_commit_sha)

    # Step 5: Check the response
    assert result["status"] == "blocked"
    assert "notes.txt" in result["files"]

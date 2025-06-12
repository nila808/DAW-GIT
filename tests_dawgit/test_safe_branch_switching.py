import ui_strings
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from git import Repo
from daw_git_gui import DAWGitApp

def test_prevent_branch_switch_with_uncommitted_changes(tmp_path):

    # ✅ Setup real repo
    project_file = tmp_path / "track.als"
    project_file.write_text("Initial version")
    repo = Repo.init(tmp_path)
    repo.index.add(["track.als"])
    repo.index.commit("init")
    repo.git.branch("new-branch")

    # Simulate uncommitted changes
    project_file.write_text("Uncommitted change")

    app = DAWGitApp(project_path=tmp_path, build_ui=False)

    # ✅ Patch UI for headless
    from PyQt6.QtWidgets import QLabel
    app.branch_label = QLabel()
    app.commit_label = QLabel()
    app.update_status_label = lambda: None

    app.init_git()
    assert app.repo is not None

    result = app.safe_switch_branch("new-branch")

    # assert result["status"] == "blocked"
    assert result["status"] == "warning"
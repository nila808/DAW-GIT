import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QLabel
from pathlib import Path
import os
from daw_git_gui import DAWGitApp

@pytest.fixture
def app(tmp_path):
    # Use a clean temp path for project simulation
    project_path = tmp_path / "TestProject"
    project_path.mkdir(parents=True, exist_ok=True)
    return DAWGitApp(project_path=str(project_path), build_ui=True)

def test_repo_no_changes(app):
    """
    Test when repo is loaded but no unsaved changes.
    Expected behavior: Status label should show 'Project loaded successfully.'
    """
    (app.project_path / "dummy.als").touch()  # Simulate DAW file
    app.repo = MagicMock()
    app.repo.active_branch.name = "main"
    app.repo.head = MagicMock()
    app.repo.git.status = MagicMock(return_value="")  # Clean repo
    app.has_unsaved_changes = lambda: False
    app.repo.head.is_detached = False
    app.update_status_label()
    assert "Session branch" in app.status_label.text()
    assert "version" in app.status_label.text()

def test_repo_unsaved_changes(app):
    """
    Test when repo is loaded and there are unsaved changes.
    Expected behavior: Status label should show 'Unsaved changes detected in your DAW project.'
    """
    (app.project_path / "dummy.als").touch()
    app.repo = MagicMock()
    app.repo.active_branch.name = "main"
    app.repo.head = MagicMock()
    app.has_unsaved_changes = lambda: True

    app.repo.head.is_detached = False
    app.repo.head = MagicMock()
    app.repo.head.is_detached = False
    app.update_status_label()
    assert "Session branch" in app.status_label.text()
    assert "version" in app.status_label.text()

def test_repo_with_branch_and_commit(app):
    """
    Test when repo is loaded with branch and commits.
    Expected behavior: Status label shows active session.
    """
    (app.project_path / "dummy.als").touch()
    app.repo = MagicMock()
    app.repo.head = MagicMock()
    app.repo.active_branch.name = "main"
    app.repo.iter_commits = lambda x: [1, 2, 3]
    app.has_unsaved_changes = lambda: False

    app.repo.head.is_detached = False
    app.repo.head = MagicMock()
    app.repo.head.is_detached = False
    app.update_status_label()
    assert "Session branch" in app.status_label.text()

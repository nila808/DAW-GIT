import ui_strings
import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QLabel
from pathlib import Path
from daw_git_gui import DAWGitApp

@pytest.fixture
def app(tmp_path):
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir(parents=True, exist_ok=True)
    return DAWGitApp(project_path=str(project_path), build_ui=True)

def test_repo_no_changes(app):
    (app.project_path / ui_strings.DUMMY_ALS_FILE).touch()
    app.repo = MagicMock()
    app.repo.active_branch.name = "main"
    app.repo.head = MagicMock()
    app.repo.git.status = MagicMock(return_value="")
    app.repo.head.is_detached = False
    app.repo.head.commit.hexsha = "abc123"
    app.repo.commit = lambda ref: MagicMock(hexsha="abc123")
    app.has_unsaved_changes = lambda: False

    app.update_status_label()
    text = app.status_label.text()

    assert "Version Line" in text
    assert "Take" in text

def test_repo_unsaved_changes(app):
    (app.project_path / ui_strings.DUMMY_ALS_FILE).touch()
    app.repo = MagicMock()
    app.repo.active_branch.name = "main"
    app.repo.head = MagicMock()
    app.repo.head.is_detached = False
    app.repo.head.commit.hexsha = "abc123"
    app.repo.commit = lambda ref: MagicMock(hexsha="abc123")
    app.has_unsaved_changes = lambda: True

    app.update_status_label()
    text = app.status_label.text()

    assert "Version Line" in text
    assert "Take" in text

def test_repo_with_branch_and_commit(app):
    (app.project_path / ui_strings.DUMMY_ALS_FILE).touch()
    app.repo = MagicMock()
    app.repo.head = MagicMock()
    app.repo.active_branch.name = "main"
    app.repo.iter_commits = lambda branch: [1, 2, 3]
    app.repo.head.is_detached = False
    app.repo.head.commit.hexsha = "abc123"
    app.repo.commit = lambda ref: MagicMock(hexsha="abc123")
    app.has_unsaved_changes = lambda: False

    app.update_status_label()
    text = app.status_label.text()

    assert "Version Line" in text
    assert "Take" in text

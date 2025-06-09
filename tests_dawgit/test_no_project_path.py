import ui_strings
import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QLabel
from pathlib import Path
from daw_git_gui import DAWGitApp

@pytest.fixture
def app(tmp_path):
    # Use a clean temp path for project simulation
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir(parents=True, exist_ok=True)
    return DAWGitApp(project_path=str(project_path), build_ui=True)

def mock_valid_repo(app):
    app.repo = MagicMock()
    app.repo.head.is_detached = False
    app.repo.commit.return_value = MagicMock(hexsha="dummysha")
    app.repo.branches = [MagicMock(name="main")]
    app.repo.active_branch = MagicMock()
    app.repo.active_branch.commit = app.repo.commit.return_value

def test_repo_no_changes(app):
    """
    Test when repo is loaded but no unsaved changes.
    Expected behavior: Status label should show 'Version Line'
    """
    (app.project_path / ui_strings.DUMMY_ALS_FILE).touch()
    mock_valid_repo(app)
    app.repo.git.status = MagicMock(return_value="")  # Clean repo
    app.has_unsaved_changes = lambda: False

    app.update_status_label()

    assert "Version Line" in app.status_label.text()
    assert "version" in app.status_label.text()


def test_repo_unsaved_changes(app):
    """
    Test when repo is loaded and there are unsaved changes.
    Expected behavior: Status label should show 'Version Line' and 'version'
    """
    (app.project_path / ui_strings.DUMMY_ALS_FILE).touch()
    mock_valid_repo(app)
    app.has_unsaved_changes = lambda: True

    app.update_status_label()

    assert "Version Line" in app.status_label.text()
    assert "version" in app.status_label.text()


def test_repo_with_branch_and_commit(app):
    """
    Test when repo is loaded with branch and commits.
    Expected behavior: Status label shows active version line.
    """
    (app.project_path / ui_strings.DUMMY_ALS_FILE).touch()
    mock_valid_repo(app)
    app.repo.iter_commits = lambda x: [1, 2, 3]
    app.has_unsaved_changes = lambda: False

    app.update_status_label()

    assert "Version Line" in app.status_label.text()
    assert "version" in app.status_label.text()

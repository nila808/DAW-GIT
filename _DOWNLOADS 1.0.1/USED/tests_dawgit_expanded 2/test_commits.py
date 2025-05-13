import os
import pytest
from daw_git_gui import *  # Assumes imported correctly


@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_als_file(temp_repo_factory):
    """TODO: Implement logic for def test_commit_requires_als_file(temp_repo_factory): test."""
    pass


@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_on_detached_head_warns_user(temp_repo_factory):
    """TODO: Implement logic for def test_commit_on_detached_head_warns_user(temp_repo_factory): test."""
    pass


@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_to_branch_creates_tag(temp_repo_factory):
    """TODO: Implement logic for def test_commit_to_branch_creates_tag(temp_repo_factory): test."""
    pass


import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp, Repo, QTestAppWrapper

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_als_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # No .als file
    Path(repo_path, "readme.txt").write_text("This is not a project")

    # Launch app
    app = QTestAppWrapper(repo_path, qtbot)

    # Try to commit and expect it to be blocked
    result = app.commit_changes()
    assert result is False or "als" in app.status_message.lower()

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_logicx_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # No .logicx file
    Path(repo_path, "notes.txt").write_text("Not a DAW project")

    # Launch app
    app = QTestAppWrapper(repo_path, qtbot)

    # Try to commit and expect it to be blocked
    result = app.commit_changes()
    assert result is False or "logicx" in app.status_message.lower()

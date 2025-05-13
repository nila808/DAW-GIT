import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_als_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    Path(repo_path, "readme.txt").write_text("This is not a project")

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    result = app.commit_changes()
    status = app.status_label.text().lower()
    assert result is False or "als" in status

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_logicx_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    Path(repo_path, "notes.txt").write_text("Not a DAW project")

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    result = app.commit_changes()
    status = app.status_label.text().lower()
    assert result is False or "logicx" in status
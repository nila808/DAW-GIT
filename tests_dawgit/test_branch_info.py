import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_create_new_branch_from_commit(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Create initial commit
    als_file = Path(repo_path) / "project.als"
    als_file.write_text("Dummy ALS content")
    repo.git.add(all=True)
    repo.git.commit(m="Initial commit")

    # Detach HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    app.create_new_version_line("test_branch")

    # ✅ Use updated app.repo here
    assert not app.repo.head.is_detached

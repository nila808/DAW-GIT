import os
import pytest
from pathlib import Path
from unittest import mock
from daw_git_gui import DAWGitApp
from git import Repo

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_checkout_commit_from_other_branch(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    Path(repo_path, "track.als").write_text("v1")
    repo.git.add(all=True)
    repo.git.commit(m="v1")

    repo.git.checkout("-b", "branch-explore")
    Path(repo_path, "track.als").write_text("v2")
    repo.git.add(all=True)
    repo.git.commit(m="v2")

    first_commit = repo.git.rev_list("main", max_count=1)
    repo.git.checkout(first_commit)

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    app.checkout_selected_commit(first_commit)

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
@mock.patch("subprocess.Popen")
def test_open_latest_daw_project_launches_correct_file(mock_popen, temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    als_file = Path(repo_path, "session.als")
    als_file.write_text("Ableton project file")
    repo.git.add(all=True)
    repo.git.commit(m="commit als")

    repo.git.checkout(repo.head.commit.hexsha)
    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    app.checkout_selected_commit(repo.head.commit.hexsha)
    app.open_latest_daw_project()

    mock_popen.assert_called_once()
    args = mock_popen.call_args[0][0]
    assert "session.als" in " ".join(args)
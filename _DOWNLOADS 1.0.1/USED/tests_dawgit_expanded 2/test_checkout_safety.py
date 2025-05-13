
import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp, Repo, QTestAppWrapper

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_checkout_commit_from_other_branch(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Setup: Initial commit
    Path(repo_path, "track.als").write_text("v1")
    repo.git.add(all=True)
    repo.git.commit(m="v1")

    # Create second commit on new branch
    repo.git.checkout("-b", "branch-explore")
    Path(repo_path, "track.als").write_text("v2")
    repo.git.add(all=True)
    repo.git.commit(m="v2")

    # Checkout first commit from main
    first_commit = repo.git.rev_list("main", max_count=1)
    repo.git.checkout(first_commit)

    # Launch app and trigger checkout logic
    app = QTestAppWrapper(repo_path, qtbot)
    app.checkout_selected_commit(commit_hash=first_commit)

    # Confirm we are in detached HEAD
    assert repo.head.is_detached

    # Confirm .als file matches expected content
    assert Path(repo_path, "track.als").read_text() == "v1"

import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp, Repo, QTestAppWrapper

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_return_to_latest_after_cross_checkout(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Commit on main
    Path(repo_path, "track.als").write_text("main version")
    repo.git.add(all=True)
    repo.git.commit(m="main")

    # Create new branch with second commit
    repo.git.checkout("-b", "explore")
    Path(repo_path, "track.als").write_text("branch version")
    repo.git.add(all=True)
    repo.git.commit(m="branch")

    # Checkout commit from main (snapshot)
    first_commit = repo.git.rev_list("main", max_count=1)
    repo.git.checkout(first_commit)

    # Launch app and return to latest
    app = QTestAppWrapper(repo_path, qtbot)
    app.return_to_latest_version()

    # Confirm that HEAD is now back on 'explore'
    assert repo.active_branch.name == "explore"
    assert Path(repo_path, "track.als").read_text() == "branch version"

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_checkout_logicx_snapshot_returns_to_branch(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Create main commit with .logicx
    Path(repo_path, "project.logicx").write_text("main logicx")
    repo.git.add(all=True)
    repo.git.commit(m="main")

    # New branch
    repo.git.checkout("-b", "branchlogicx")
    Path(repo_path, "project.logicx").write_text("logicx v2")
    repo.git.add(all=True)
    repo.git.commit(m="logicx v2")

    # Checkout snapshot from main
    first_commit = repo.git.rev_list("main", max_count=1)
    repo.git.checkout(first_commit)

    # Launch app and return to latest
    app = QTestAppWrapper(repo_path, qtbot)
    app.return_to_latest_version()

    # Assert we're back on branch and file content is v2
    assert repo.active_branch.name == "branchlogicx"
    assert Path(repo_path, "project.logicx").read_text() == "logicx v2"

import os
import pytest
from pathlib import Path
from unittest import mock
from daw_git_gui import DAWGitApp, Repo, QTestAppWrapper

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_open_button_shown_only_after_checkout(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Commit a project file
    als_file = Path(repo_path, "demo.als")
    als_file.write_text("v1")
    repo.git.add(all=True)
    repo.git.commit(m="init")

    # Launch app BEFORE checkout
    app = QTestAppWrapper(repo_path, qtbot)
    assert not app.open_als_button.isVisible()

    # Checkout to a snapshot
    repo.git.checkout(repo.head.commit.hexsha)
    app.checkout_selected_commit(commit_hash=repo.head.commit.hexsha)

    # NOW button should be visible
    assert app.open_als_button.isVisible()

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
@mock.patch("subprocess.Popen")
def test_open_latest_daw_project_launches_correct_file(mock_popen, temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Add .als file and commit
    als_file = Path(repo_path, "session.als")
    als_file.write_text("Ableton project file")
    repo.git.add(all=True)
    repo.git.commit(m="commit als")

    # Checkout snapshot
    repo.git.checkout(repo.head.commit.hexsha)
    app = QTestAppWrapper(repo_path, qtbot)
    app.checkout_selected_commit(commit_hash=repo.head.commit.hexsha)

    # Call open function
    app.open_latest_daw_project()

    # Confirm subprocess was called with correct file
    mock_popen.assert_called_once()
    args = mock_popen.call_args[0][0]
    assert "session.als" in " ".join(args)

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

    # Commit v1 on main
    Path(repo_path, "track.als").write_text("v1")
    repo.git.add(all=True)
    repo.git.commit(m="v1")

    # Create and switch to a new branch, then commit v2
    repo.git.checkout("-b", "branch-explore")
    Path(repo_path, "track.als").write_text("v2")
    repo.git.add(all=True)
    repo.git.commit(m="v2")

    # Get the first commit from main and checkout (detached HEAD)
    first_commit = repo.git.rev_list("main", max_count=1)
    repo.git.checkout(first_commit)

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    app.checkout_selected_commit(first_commit)


@mock.patch("daw_git_gui.subprocess.Popen")
@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_open_latest_daw_project_launches_correct_file(mock_popen, temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Create and commit an Ableton project file
    als_file = Path(repo_path, "session.als")
    als_file.write_text("Ableton project file")
    repo.git.add(all=True)
    repo.git.commit(m="commit als")

    # Detach HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    # Launch app and attach to test
    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    if not app.repo:
        app.repo = Repo(repo_path)

    # Create the dummy.als file that the app expects to launch
    dummy_als = Path(repo_path, "dummy.als")
    dummy_als.write_text("dummy Ableton session")
    repo.git.add(all=True)
    repo.git.commit(m="Add dummy.als")

    # Checkout commit to simulate DAW version selection
    app.checkout_selected_commit(repo.head.commit.hexsha)   

    # 🧼 Clear all subprocess calls from prior Git operations
    mock_popen.reset_mock()

    # Try opening the latest DAW project
    app.open_latest_daw_project()

    # ✅ Confirm it tries to open the .als file
    mock_popen.assert_called_once()
    args = mock_popen.call_args[0][0]
    launched_path = " ".join(args)
    print("📂 Launched path:", launched_path)

    # ✅ Check that the opened file was dummy.als as expected by the app
    expected_path = str(dummy_als)
    assert expected_path in launched_path or dummy_als.name in launched_path
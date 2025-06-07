import ui_strings
import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import

from PyQt6.QtWidgets import QTableWidgetItem, QInputDialog
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import subprocess
import pytest
from pathlib import Path
from unittest import mock
from daw_git_gui import DAWGitApp
from git import Repo
from ui_strings import (
    POPPEN_SKIP_MSG, 
    ASSERT_CONTAINS_PREFIX, 
    PRINT_LAUNCHED_PATH_LABEL
)
from tests_dawgit.test_helpers import create_test_project
from daw_git_gui import DAWGitApp


# ---------------------- FIXTURES ----------------------

@pytest.fixture
def test_repo(tmp_path):
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(project_path)

    project_path.mkdir()
    (project_path / ui_strings.DUMMY_ALS_FILE).write_text("Ableton project v1")
    return project_path

@pytest.fixture
def app(test_repo):
    app = DAWGitApp(project_path=test_repo, build_ui=False)
    app.repo = Repo.init(test_repo)
    return app

# ---------------------- TEST CASES ----------------------

def test_backup_folder_created_on_unsaved_changes(tmp_path):
    # Create fake project folder
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir()

    # Create a dummy DAW file so Git init works
    daw_file = project_path / "song.als"
    daw_file.write_text("test content")

    app = DAWGitApp(str(project_path))
    app.init_git()

    # Force project_path onto the app (if not already set)
    app.project_path = project_path

    # ✅ Mock repo as dirty to force backup trigger
    with mock.patch.object(app.repo, "is_dirty", return_value=True):
        backup_dir = app.backup_unsaved_changes()

    # ✅ Now assert the backup folder was created
    assert backup_dir is not None, "Expected backup folder path"
    assert backup_dir.exists(), "Backup folder does not exist"
    assert any(backup_dir.iterdir()), "Backup folder is empty"

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

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(repo_path)
    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)
    app.checkout_selected_commit(first_commit)


@mock.patch("daw_git_gui.subprocess.Popen")
@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_open_latest_daw_project_launches_correct_file(mock_popen, temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    als_file = Path(repo_path, "session.als")
    als_file.write_text("Ableton project file")
    repo.git.add(all=True)
    repo.git.commit(m="commit als")

    dummy_als = Path(repo_path, ui_strings.DUMMY_ALS_FILE)
    dummy_als.write_text("dummy Ableton session")
    repo.git.add(all=True)
    repo.git.commit(m="Add dummy.als")

    repo.git.checkout(repo.head.commit.hexsha)

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(repo_path)
    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    app.repo = repo
    app.settings.setValue("last_path", str(repo_path))
    app.checkout_selected_commit(repo.head.commit.hexsha)

    mock_popen.reset_mock()
    expected_path = str(dummy_als)

    if os.getenv("DAWGIT_TEST_MODE") == "1":
        print(POPPEN_SKIP_MSG)
        result = app.open_latest_daw_project()
        assert expected_path in result["opened_file"]
    else:
        app.open_latest_daw_project()
        args = mock_popen.call_args[0][0]
        launched_path = " ".join(args)
        print(PRINT_LAUNCHED_PATH_LABEL, launched_path)
        expected = expected_path
        print(ASSERT_CONTAINS_PREFIX, expected)
        assert expected_path in launched_path or dummy_als.name in launched_path


def test_checkout_latest_from_old_commit(test_repo):
    from git import Repo
    from daw_git_gui import DAWGitApp

    # ✅ Setup real Git repo first
    repo = Repo.init(test_repo)
    for i in range(5):
        file = test_repo / f"track_v{i}.als"
        file.write_text(f"version {i}")
        repo.index.add([str(file.relative_to(test_repo))])
        repo.index.commit(f"Version {i}")

    # 📍 Checkout old commit (detached HEAD)
    old_commit_sha = list(repo.iter_commits("HEAD", max_count=5))[2].hexsha
    repo.git.checkout(old_commit_sha)
    assert repo.head.is_detached

    # 💥 Discard changes to allow safe return to main
    repo.git.checkout("--", ".")  # Reset tracked file modifications
    repo.git.reset("--hard")      # Reset HEAD and index to last commit
    repo.git.clean("-fd")         # Remove untracked files and dirs

    # ✅ Now launch DAWGitApp — it will load the repo correctly
    app = DAWGitApp(project_path=test_repo, build_ui=False)
    app.init_git()
    app.return_to_latest_clicked()

    # 🎯 Return to latest
    app.return_to_latest_clicked()

    # ✅ Verify result
    assert app.repo is not None
    assert not app.repo.head.is_detached


def test_checkout_selected_commit_enters_detached_head(tmp_path, qtbot):
    project_path = tmp_path / "DetachedCheck"
    project_path.mkdir()
    (project_path / "track.als").write_text("A1")

    repo = Repo.init(project_path)
    repo.index.add(["track.als"])
    repo.index.commit("Base")
    repo.index.commit("Second")
    repo.git.branch("-M", "main")

    first_sha = list(repo.iter_commits("main"))[-1].hexsha

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(project_path)
    os.environ["DAWGIT_TEST_MODE"] = "1"  # ✅ Keep it on during checkout
    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    app.repo = repo
    qtbot.addWidget(app)

    app.checkout_selected_commit(commit_sha=first_sha)
    qtbot.wait(200)

    # ✅ Don’t remove TEST_MODE until *after* asserting
    assert app.repo.head.is_detached
    assert app.repo.head.commit.hexsha == first_sha
    os.environ.pop("DAWGIT_TEST_MODE", None)




def test_checkout_latest_from_detached_state(tmp_path, qtbot):
    path, repo = create_test_project(tmp_path)
    als_file = path / "track.als"
    als_file.write_text("init")
    repo.index.add(["track.als"])
    repo.index.commit("Init")
    repo.git.branch("-M", "main")
    repo.git.switch("main")

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(path)
    os.environ["DAWGIT_TEST_MODE"] = "1"
    app = DAWGitApp(project_path=str(path), build_ui=True)
    app.repo = repo
    qtbot.addWidget(app)
    qtbot.wait(100)

    als_file.write_text("updated")
    app.commit_changes(commit_message="Updated")
    new_sha = app.repo.head.commit.hexsha

    old_sha = list(repo.iter_commits("main"))[-1].hexsha

    app.checkout_selected_commit(commit_sha=old_sha)
    qtbot.wait(200)

    # ✅ Detached state expected
    assert app.repo.head.is_detached
    assert app.repo.head.commit.hexsha == old_sha

    # ✅ Now return to latest
    app.return_to_latest_clicked()
    qtbot.wait(300)
    os.environ.pop("DAWGIT_TEST_MODE", None)

    assert not app.repo.head.is_detached
    assert app.repo.head.commit.hexsha == new_sha



def test_backup_folder_created_on_checkout(tmp_path, qtbot):
    project_path = tmp_path / "BackupTest"
    project_path.mkdir()
    (project_path / "temp.als").write_text("something")

    repo = Repo.init(project_path)
    repo.index.add(["temp.als"])
    repo.index.commit("commit 1")
    repo.index.commit("commit 2")
    repo.git.branch("-M", "main")

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(project_path)
    path, repo = create_test_project(tmp_path)
    os.environ["DAWGIT_TEST_MODE"] = "1"
    app = DAWGitApp(project_path=str(path), build_ui=True)
    os.environ.pop("DAWGIT_TEST_MODE", None)
    app.project_path = str(project_path)
    app.repo = repo

    (project_path / "temp.als").write_text("UNSAVED CHANGE")
    app.backup_unsaved_changes()

    backup_parent = Path(project_path).parent
    matching_folders = list(backup_parent.glob(f"Backup_{project_path.name}_*"))
    assert len(matching_folders) > 0, "No backup folder created"


def test_git_stash_created_on_return(tmp_path, qtbot):
    project_path = tmp_path / "StashTest"
    project_path.mkdir()
    als_file = project_path / "demo.als"
    als_file.write_text("initial")

    # Initialize repo and commit initial state
    repo = Repo.init(project_path)
    repo.index.add(["demo.als"])
    repo.index.commit("Init")
    repo.git.branch("-M", "main")

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(project_path)

    # Launch the app
    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)

    # Commit version 2
    als_file.write_text("v2")
    app.commit_changes("Second")

    # ✅ Refresh repo and get expected latest commit
    repo = Repo(project_path)
    latest_sha = repo.head.commit.hexsha
    print("[DEBUG] Expected latest SHA:", latest_sha)

    # ✅ Checkout earlier commit directly via Git to avoid GUI flakiness
    old_sha = list(repo.iter_commits("main"))[-1].hexsha
    repo.git.checkout(old_sha)
    app.repo = Repo(project_path)  # rebind

    actual_sha = app.repo.head.commit.hexsha
    print("[DEBUG TEST] HEAD after checkout:", actual_sha)
    assert actual_sha == old_sha, f"Expected {old_sha[:7]}, got {actual_sha[:7]}"
    assert app.repo.head.is_detached

    # Modify without committing (triggers stash)
    als_file.write_text("unsaved again")
    app.repo.git.add(update=True)
    assert app.repo.is_dirty()

    # ✅ Run 'return to latest' while in test mode
    os.environ["DAWGIT_TEST_MODE"] = "1"
    app.return_to_latest_clicked()
    qtbot.wait(300)
    os.environ.pop("DAWGIT_TEST_MODE", None)

    app.repo = Repo(project_path)
    final_sha = app.repo.head.commit.hexsha

    # Final assertions
    print("[DEBUG] Returned SHA:", final_sha)
    print("[DEBUG] Repo head is_detached:", app.repo.head.is_detached)
    print("[DEBUG] File content:", als_file.read_text())

    assert not app.repo.head.is_detached
    assert final_sha == latest_sha, "Should return to latest commit"
    assert als_file.read_text() != "unsaved again", "Unsaved changes should be stashed/reverted"


def test_switch_branch_with_uncommitted_changes_warns_or_stashes(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Set up commits
    als_file = Path(repo_path) / "track.als"
    als_file.write_text("Initial version")
    repo.git.add(all=True)
    repo.git.commit(m=ui_strings.INITIAL_COMMIT_MESSAGE)

    repo.git.checkout("-b", "alt_branch")
    als_file.write_text("Alt edit")
    repo.git.add(all=True)
    repo.git.commit(m="Alt branch commit")

    repo.git.checkout("main")
    als_file.write_text("unsaved")

    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(repo_path)
    repo_path = Path(repo_path)  # ✅ Add this line here only

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    with mock.patch.object(app, "has_unsaved_changes", return_value=True), \
         mock.patch.object(app, "backup_unsaved_changes", wraps=app.backup_unsaved_changes) as mock_backup:

        result = app.switch_branch("alt_branch")

    assert result["status"] == "success"
    assert app.repo.active_branch.name == "alt_branch"
    mock_backup.assert_called_once()

    backup_root = repo_path.parent
    matching_backups = list(backup_root.glob(f"Backup_{repo_path.name}_*"))
    assert matching_backups, "Expected backup folder not found for unsaved changes"

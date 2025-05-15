import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pathlib import Path
from unittest import mock
from daw_git_gui import DAWGitApp
from git import Repo

# ---------------------- FIXTURES ----------------------

@pytest.fixture
def test_repo(tmp_path):
    project_path = tmp_path / "TestProject"
    project_path.mkdir()
    (project_path / "dummy.als").write_text("Ableton project v1")
    return project_path

@pytest.fixture
def app(test_repo):
    app = DAWGitApp(project_path=test_repo, build_ui=False)
    app.repo = Repo.init(test_repo)
    return app

# ---------------------- TEST CASES ----------------------

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


@mock.patch("daw_git_gui.subprocess.Popen")
@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_open_latest_daw_project_launches_correct_file(mock_popen, temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    als_file = Path(repo_path, "session.als")
    als_file.write_text("Ableton project file")
    repo.git.add(all=True)
    repo.git.commit(m="commit als")

    dummy_als = Path(repo_path, "dummy.als")
    dummy_als.write_text("dummy Ableton session")
    repo.git.add(all=True)
    repo.git.commit(m="Add dummy.als")

    repo.git.checkout(repo.head.commit.hexsha)

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    app.repo = repo
    app.settings.setValue("last_path", str(repo_path))
    app.checkout_selected_commit(repo.head.commit.hexsha)

    mock_popen.reset_mock()
    app.open_latest_daw_project()

    args = mock_popen.call_args[0][0]
    launched_path = " ".join(args)
    expected_path = str(dummy_als)
    print("📂 Launched path:", launched_path)
    print("✅ Should contain:", expected_path)

    assert expected_path in launched_path or dummy_als.name in launched_path


def test_checkout_latest_from_old_commit(app, test_repo):
    for i in range(5):
        file = test_repo / f"track_v{i}.als"
        file.write_text(f"version {i}")
        app.repo.index.add([str(file.relative_to(test_repo))])
        app.repo.index.commit(f"Version {i}")

    app.repo = Repo(test_repo)

    all_commits = list(app.repo.iter_commits("HEAD", max_count=5))
    old_commit_sha = all_commits[2].hexsha

    app.repo.git.checkout(old_commit_sha)
    assert app.repo.head.is_detached

    app.checkout_latest()

    assert not app.repo.head.is_detached
    assert app.repo.active_branch.name in ["main", "master"]
    latest_commit_sha = next(app.repo.iter_commits("HEAD", max_count=1)).hexsha
    assert app.repo.head.commit.hexsha == latest_commit_sha


def test_checkout_selected_commit_enters_detached_head(tmp_path, qtbot):
    project_path = tmp_path / "DetachedCheck"
    project_path.mkdir()
    (project_path / "track.als").write_text("A1")

    repo = Repo.init(project_path)
    repo.index.add(["track.als"])
    repo.index.commit("Base")
    repo.index.commit("Second")
    repo.git.branch("-M", "main")

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    first_sha = list(repo.iter_commits("main"))[-1].hexsha
    app.checkout_selected_commit(commit_sha=first_sha)

    assert app.repo.head.is_detached
    assert app.repo.head.commit.hexsha == first_sha


def test_checkout_latest_from_detached_state(tmp_path, qtbot):
    project_path = tmp_path / "ReturnTest"
    project_path.mkdir()
    als_file = project_path / "music.als"
    als_file.write_text("init")

    repo = Repo.init(project_path)
    repo.index.add(["music.als"])
    repo.index.commit("Init")
    repo.git.branch("-M", "main")

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    als_file.write_text("updated")
    app.repo.git.switch("main")
    app.commit_changes(commit_message="Updated")
    new_sha = app.repo.head.commit.hexsha

    old_sha = list(repo.iter_commits("main"))[-1].hexsha
    app.checkout_selected_commit(commit_sha=old_sha)
    assert app.repo.head.commit.hexsha == old_sha
    assert app.repo.head.is_detached

    app.checkout_latest()
    app.repo = Repo(project_path)
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

    app = DAWGitApp()
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

    repo = Repo.init(project_path)
    repo.index.add(["demo.als"])
    repo.index.commit("Init")
    repo.git.branch("-M", "main")

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    als_file.write_text("new")
    app.repo.git.switch("main")
    app.commit_changes(commit_message="Second")
    latest_sha = app.repo.head.commit.hexsha

    old_sha = list(repo.iter_commits("main"))[-1].hexsha
    app.checkout_selected_commit(commit_sha=old_sha)
    assert app.repo.head.commit.hexsha == old_sha

    als_file.write_text("unsaved again")
    app.checkout_latest()
    app.repo = Repo(project_path)

    assert not app.repo.head.is_detached
    assert app.repo.head.commit.hexsha == latest_sha

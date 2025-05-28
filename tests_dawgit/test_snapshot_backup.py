import os
os.environ["DAWGIT_TEST_MODE"] = "1"

import shutil
from pathlib import Path
from git import Repo
from unittest.mock import patch
from PyQt6.QtWidgets import QMessageBox
from daw_git_gui import DAWGitApp
from daw_git_core import backup_latest_commit_state

def test_snapshot_backup_created_on_checkout(tmp_path, qtbot):
    # Set up fake project and repo
    project_path = tmp_path / "MyTrack"
    project_path.mkdir()

    # Create test files
    als_file = project_path / "myproject.als"
    sample_file = project_path / "kick.wav"
    als_file.write_text("test als")
    sample_file.write_text("test kick")

    # Init repo and commit
    repo = Repo.init(project_path)
    repo.index.add(["myproject.als", "kick.wav"])
    repo.index.commit("Initial snapshot")

    # Add a second commit
    second_file = project_path / "snare.wav"
    second_file.write_text("snare test")
    repo.index.add(["snare.wav"])
    repo.index.commit("Second snapshot")

    # Launch app
    app = DAWGitApp()
    qtbot.addWidget(app)
    app.project_path = project_path
    app.repo = repo
    app.custom_env = lambda: {}  # No-op

    # Monkeypatch dialogs
    with patch.object(QMessageBox, 'warning'), \
        patch.object(QMessageBox, 'information'), \
        patch.object(QMessageBox, 'critical'):

        # Run the backup-triggering method
        sha = repo.git.rev_list("--max-parents=0", "HEAD").splitlines()[0]
        pre_checkout_sha = repo.head.commit.hexsha  # ✅ Save HEAD before checkout

        app.checkout_selected_commit(commit_sha=sha)

        # Set path and print debug
        cache_path = project_path / ".dawgit_cache" / "latest_snapshot" / pre_checkout_sha

        print(f"[DEBUG] Expected cache path: {cache_path}")
        print(f"[DEBUG] Cache path exists? {cache_path.exists()}")
        print(f"[DEBUG] Contents: {list(cache_path.parent.glob('*'))}")

        # Confirm backup folder created
        assert cache_path.exists()
        assert (cache_path / "myproject.als").exists()
        assert (cache_path / "kick.wav").exists()

def test_backup_skipped_if_exists(tmp_path):
    from daw_git_core import backup_latest_commit_state

    # Setup fake project
    project_path = tmp_path / "TrackTest"
    project_path.mkdir()
    als_file = project_path / "test.als"
    als_file.write_text("session 1")

    # Init repo
    repo = Repo.init(project_path)
    repo.index.add(["test.als"])
    repo.index.commit("Initial")

    # First backup
    sha = repo.head.commit.hexsha
    backup_latest_commit_state(repo, project_path, sha)

    # Confirm it exists
    backup_path = project_path / ".dawgit_cache" / "latest_snapshot" / sha
    assert backup_path.exists()

    # Create a file in the backup to track overwrite behavior
    marker = backup_path / "marker.txt"
    marker.write_text("DO NOT OVERWRITE")

    # Run backup again — should skip
    backup_latest_commit_state(repo, project_path, sha)

    # Confirm marker file still exists — untouched
    assert marker.read_text() == "DO NOT OVERWRITE"


def test_audio_files_backed_up_on_switch(tmp_path, qtbot):
    # Setup: Create fake project
    project_path = tmp_path / "BackupTest"
    project_path.mkdir()
    als_file = project_path / "mytrack.als"
    als_file.write_text("test content")

    # Init repo
    repo = Repo.init(project_path)
    repo.index.add(["mytrack.als"])
    repo.index.commit("Initial commit")
    repo.git.branch("-M", "main")
    initial_sha = repo.head.commit.hexsha

    # App setup
    app = DAWGitApp(project_path=str(project_path), build_ui=False)
    app.repo = repo
    app.git.repo = repo

    # Trigger backup manually
    backup_latest_commit_state(app.repo, project_path, commit_sha=initial_sha)

    # Assert file exists in backup location
    backup_file = project_path / ".dawgit_cache" / "latest_snapshot" / initial_sha / "mytrack.als"
    assert backup_file.exists(), "Expected .als file not found in snapshot backup."
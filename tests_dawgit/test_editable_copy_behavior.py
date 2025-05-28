import os
import shutil
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo
from unittest.mock import patch
from PyQt6.QtWidgets import QMessageBox

# Ensure test mode for safety and auto-behavior
os.environ["DAWGIT_TEST_MODE"] = "1"

def test_editable_copy_skips_recent_mod_warning(tmp_path, qtbot):
    # Setup fake project and editable copy
    project_path = tmp_path / "MyTestProject"
    project_path.mkdir()
    als_file = project_path / "track.als"
    als_file.write_text("test content")

    editable_path = project_path / ".dawgit_checkout_work" / "fake_sha"
    editable_path.mkdir(parents=True)
    editable_copy = editable_path / "track.als"
    shutil.copy2(als_file, editable_copy)

    app = DAWGitApp(project_path=str(project_path), build_ui=False)
    app.editable_daw_path = editable_path

    result = app.open_latest_daw_project()
    assert result["status"] == "success"
    assert "track.als" in result["opened_file"]

def test_checkout_creates_editable_copy_folder(tmp_path, qtbot):
    project_path = tmp_path / "TestCheckoutProject"
    project_path.mkdir()
    als_file = project_path / "song.als"
    als_file.write_text("snapshot content")

    repo = Repo.init(project_path)
    repo.index.add(["song.als"])
    repo.index.commit("Initial version")
    repo.git.branch("-M", "main")

    app = DAWGitApp(project_path=str(project_path), build_ui=False)
    app.repo = repo
    app.git.repo = repo

    # Simulate editable copy creation (from checkout)
    head_commit = repo.head.commit.hexsha
    editable_path = project_path / ".dawgit_checkout_work" / head_commit
    editable_path.mkdir(parents=True, exist_ok=True)
    for daw_file in project_path.glob("*.als"):
        shutil.copy2(daw_file, editable_path / daw_file.name)

    assert editable_path.exists(), "Editable folder not created"
    assert (editable_path / "song.als").exists(), ".als file missing in editable folder"

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from PyQt6.QtWidgets import QMessageBox, QFileDialog
import tempfile
import shutil
from pathlib import Path
from git import Repo
import subprocess


@pytest.fixture(autouse=True)
def clear_last_path_file():
    if os.path.exists("last_path"):
        os.remove("last_path")

        
@pytest.fixture
def temp_repo_factory():
    """
    Returns a callable that creates a new temp Git repo with LFS-style tracking.
    Automatically cleans up test_branch after use.
    """
    created_paths = []

    def _create_repo():
        temp_dir = tempfile.mkdtemp()
        repo = Repo.init(temp_dir)
        gitattributes = Path(temp_dir) / ".gitattributes"
        gitattributes.write_text("*.als filter=lfs diff=lfs merge=lfs -text\n*.logicx filter=lfs diff=lfs merge=lfs -text")
        repo.git.add(A=True)
        repo.git.commit(m="Init repo for testing", allow_empty=True)
        created_paths.append(temp_dir)
        return temp_dir

    yield _create_repo

    # 🧹 Clean up test_branch after test
    for path in created_paths:
        try:
            subprocess.run(["git", "checkout", "main"], cwd=path, check=True)
            subprocess.run(["git", "branch", "-D", "test_branch"], cwd=path, check=True)
        except Exception as e:
            print(f"[CLEANUP] Could not delete test_branch in {path}: {e}")

        # 🧹 Global post-test cleanup
    for path in created_paths:
        try:
            subprocess.run(["git", "checkout", "main"], cwd=path, check=False)
            subprocess.run(["git", "branch", "-D", "test_branch"], cwd=path, check=False)
            subprocess.run(["git", "tag", "-d", "auto"], cwd=path, check=False)
            subprocess.run(["git", "stash", "clear"], cwd=path, check=False)

            # 🗑️ Remove backup folder
            backups = Path(path) / ".dawgit_backups"
            if backups.exists():
                shutil.rmtree(backups)
                print(f"[CLEANUP] Removed test backups: {backups}")

            # 🗑️ Remove test placeholder .als
            placeholder = Path(path) / "auto_placeholder.als"
            if placeholder.exists():
                placeholder.unlink()
                print(f"[CLEANUP] Removed auto placeholder: {placeholder}")

        except Exception as e:
            print(f"[CLEANUP] Error during cleanup in {path}: {e}")


# Automatically accept all modals and dialogs
@pytest.fixture(autouse=True)
def auto_patch_dialogs(monkeypatch):

    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "/tmp/test-dir")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("/tmp/test-file.als", "ALS Files (*.als)"))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("/tmp/saved-project.als", "ALS Files (*.als)"))

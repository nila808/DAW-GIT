import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Activate test mode globally
os.environ["DAWGIT_TEST_MODE"] = "1"

import pytest
from PyQt6.QtWidgets import QMessageBox, QFileDialog
import tempfile
import shutil
from pathlib import Path
from git import Repo
import subprocess
from daw_git_gui import DAWGitApp



@pytest.fixture(autouse=True)
def clear_last_path_file():
    if os.path.exists("last_path"):
        os.remove("last_path")

        
@pytest.fixture
def temp_repo_factory():
    """
    Returns a callable that creates a new temp Git repo with LFS-style tracking.
    Automatically cleans up test_branch and DAW files after use.
    """
    created_paths = []

    def _create_repo():
        temp_dir = tempfile.mkdtemp()
        repo = Repo.init(temp_dir)

        # 🧹 Ensure no leftover DAW files
        for ext in ("*.als", "*.logicx"):
            for f in Path(temp_dir).glob(ext):
                f.unlink()

        # 🎼 Add LFS-style .gitattributes
        gitattributes = Path(temp_dir) / ".gitattributes"
        gitattributes.write_text("*.als filter=lfs diff=lfs merge=lfs -text\n*.logicx filter=lfs diff=lfs merge=lfs -text")

        repo.git.add(A=True)
        repo.git.commit(m="Init repo for testing", allow_empty=True)
        created_paths.append(temp_dir)
        return temp_dir

    yield _create_repo

    # 🧹 Final cleanup for each created path
    for path in created_paths:
        try:
            subprocess.run(["git", "checkout", "main"], cwd=path, check=False)
            subprocess.run(["git", "branch", "-D", "test_branch"], cwd=path, check=False)
            subprocess.run(["git", "tag", "-d", "auto"], cwd=path, check=False)
            subprocess.run(["git", "stash", "clear"], cwd=path, check=False)

            # Remove backups and placeholder files
            backups = Path(path) / ".dawgit_backups"
            if backups.exists():
                shutil.rmtree(backups)
                print(f"[CLEANUP] Removed test backups: {backups}")

            for ext in ("auto_placeholder.als", "*.als", "*.logicx"):
                for f in Path(path).glob(ext):
                    f.unlink()
                    print(f"[CLEANUP] Removed file: {f}")

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


# Helpers:
@pytest.fixture
def temp_project(tmp_path):
    """
    Provides a temporary isolated project directory for tests.
    """
    project_dir = tmp_path / "TestProject"
    project_dir.mkdir()
    return project_dir
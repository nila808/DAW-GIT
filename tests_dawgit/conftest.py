import pytest
from PyQt6.QtWidgets import QMessageBox, QFileDialog
import tempfile
import shutil
from pathlib import Path
from git import Repo


@pytest.fixture
def temp_repo_factory():
    """
    Returns a callable that creates a new temp Git repo with LFS-style tracking.
    """
    def _create_repo():
        temp_dir = tempfile.mkdtemp()
        repo = Repo.init(temp_dir)
        gitattributes = Path(temp_dir) / ".gitattributes"
        gitattributes.write_text("*.als filter=lfs diff=lfs merge=lfs -text\n*.logicx filter=lfs diff=lfs merge=lfs -text")
        repo.git.add(A=True)
        repo.git.commit(m="Init repo for testing", allow_empty=True)
        return temp_dir

    yield _create_repo

# Automatically accept all modals and dialogs
@pytest.fixture(autouse=True)
def auto_patch_dialogs(monkeypatch):
    # QMessageBox patches (already in place)
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    # QFileDialog: simulate path selection
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "/tmp/test-dir")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("/tmp/test-file.als", "ALS Files (*.als)"))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("/tmp/saved-project.als", "ALS Files (*.als)"))
import ui_strings
import os
import json
import shutil
import pytest
import uuid
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QApplication
from daw_git_gui import DAWGitApp
from git import Repo

from unittest.mock import patch
# 🧪 Disable the global fallback mock
os.environ["DAWGIT_FORCE_INPUT"] = "0"

# ✅ Patch input before importing app
patch("PyQt6.QtWidgets.QInputDialog.getText", return_value=("Alt 2", True)).start()

from daw_git_gui import DAWGitApp


from contextlib import contextmanager

os.environ["DAWGIT_TEST_MODE"] = "1"

# 🛡️ Global patch for all modal dialogs
# @pytest.fixture(autouse=True)
# def patch_dialogs(monkeypatch):
#     monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Alt 2", True))
#     monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
#     monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
#     monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: None)


@contextmanager
def working_directory(path):
    """Temporarily change working directory."""
    try:
        previous = os.getcwd()
    except FileNotFoundError:
        previous = "/tmp"
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def git_add_and_commit(repo, path: Path, filename: str, message=ui_strings.INITIAL_COMMIT_MESSAGE):
    with working_directory(path):
        repo.index.add([filename])
        repo.index.commit(message)


# ✅ Test 1: role variants
@pytest.mark.parametrize("label", ["Main Mix", "creative_take", "alt_mixdown", "my_custom_tag"])
def test_assign_commit_role_variants(monkeypatch, qtbot, label):
    project_path = Path(f"/tmp/test_tagging_{uuid.uuid4().hex}")
    project_path.mkdir(parents=True)
    (project_path / "track.als").write_text("init")

    repo = Repo.init(project_path)
    git_add_and_commit(repo, project_path, "track.als", message="init")

    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)

    sha = app.repo.head.commit.hexsha
    app.assign_commit_role(sha, label)
    app.save_commit_roles()

    role_file = project_path / ".dawgit_roles.json"
    assert role_file.exists()
    roles = json.loads(role_file.read_text())
    assert roles[sha] == label

    app.close()
    shutil.rmtree(project_path, ignore_errors=True)


# ✅ Test 2: custom tag via button
@patch("PyQt6.QtWidgets.QInputDialog.getText", return_value=("alt_2", True))
def test_tag_custom_label_assigns_alt2(mock_input, tmp_path, qtbot):
    (tmp_path / "track.als").write_text("Ableton")

    repo = Repo.init(tmp_path)
    git_add_and_commit(repo, tmp_path, "track.als", message="init")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)
    
    # 🔧 Optional: Skip QTimer logic in test mode
    if os.getenv("DAWGIT_TEST_MODE") == "1":
        app._handle_main_mix_tag = lambda: None

    sha = app.repo.head.commit.hexsha
    app.pages.switch_to("commit")
    qtbot.wait(200)

    app.commit_page.tag_custom_btn.click()
    qtbot.wait(200)

    expected_role = "alt_2"
    actual_role = app.commit_roles.get(sha)
    assert actual_role == expected_role, f"Expected '{expected_role}', got '{actual_role}'"

    role_file = tmp_path / ".dawgit_roles.json"
    assert role_file.exists()
    roles = json.loads(role_file.read_text())
    assert roles.get(sha) == expected_role

    # ✅ Force Qt event loop to flush and let all pending updates complete
    qtbot.wait(200)

    # ✅ Explicitly close the app window to release resources
    app.close()


@pytest.fixture(autouse=True)
def ensure_qapp_cleanup(qtbot):
    yield
    # ⛔ Force close all top-level widgets
    for w in QApplication.topLevelWidgets():
        if w.isVisible():
            w.close()
    qtbot.wait(100)

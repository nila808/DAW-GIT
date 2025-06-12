import ui_strings
import pytest
from unittest.mock import patch
from daw_git_gui import DAWGitApp
from git import Repo

def test_remote_connect_push(monkeypatch, tmp_path):
    # ✅ Init actual Git repo first
    repo = Repo.init(tmp_path)
    (tmp_path / "test.als").write_text("Ableton data")
    repo.index.add(["test.als"])
    repo.index.commit("init")

    # ✅ Launch DAWGitApp after repo exists
    app = DAWGitApp(project_path=tmp_path, build_ui=False)

    # ✅ Stub UI elements to prevent attr errors
    from PyQt6.QtWidgets import QLabel
    app.branch_label = QLabel()
    app.commit_label = QLabel()
    app.update_status_label = lambda: None

    app.init_git()
    assert app.repo is not None

    # ✅ Patch dialog input
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QInputDialog.getText",
        lambda *a, **kw: ("https://github.com/test/test.git", True)
    )

    # 🚀 Attempt remote connect
    app.connect_to_remote_repo()

    # ✅ Check
    assert "origin" in [r.name for r in app.repo.remotes]



def test_remote_push_failure_shows_warning(qtbot, tmp_path, monkeypatch):
    app = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(app)
    app.init_git()

    # Add dummy file and initial commit
    f = tmp_path / "session.als"
    f.write_text("init")
    app.repo.git.add("session.als")
    app.repo.index.commit("Initial")

    # Simulate user enabling remote checkbox
    app.setup_page.remote_checkbox.setChecked(True)
    qtbot.wait(50)

    # Add changes
    f.write_text("edit")
    app.repo.git.add("session.als")

    # Simulate commit message input
    app.commit_page.commit_message.setPlainText("Trigger remote push")

    # ✅ Add dummy remote to prevent 'origin' not found error
    app.repo.create_remote("origin", "https://example.com/fake.git")

    # Patch Git push to raise exception
    import subprocess

    def mock_failed_push(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0], "Simulated remote failure")

    monkeypatch.setattr("subprocess.run", mock_failed_push)

    # Capture error message from either QMessageBox.warning or critical
    triggered = {"message": ""}

    def fake_msgbox(_, title, msg):
        triggered["message"] = msg
        return

    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", fake_msgbox)
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.critical", fake_msgbox)

    app.commit_page.commit_snapshot()

    print(f"[DEBUG] MessageBox output: {triggered['message']}")
    assert "couldn’t push to remote" in triggered["message"].lower()

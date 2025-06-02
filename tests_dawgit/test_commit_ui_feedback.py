import ui_strings
import os
import sys
import json
import shutil
import pytest
import uuid
import re
from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QMessageBox

def test_empty_commit_message_blocked(qtbot, app, monkeypatch):
    """Should show a warning and block commit if message is empty."""
    app.commit_page.commit_message.setPlainText("") # Simulate empty input
    app.pages.switch_to("commit")  # optional but good UX simulation

    triggered = {"warning": False}

    def mock_warning(*args, **kwargs):
        triggered["warning"] = True
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", mock_warning)

    app.commit_changes("")  # Try to commit
    assert triggered["warning"], "Expected warning dialog for empty commit message"


def test_commit_modal_message_includes_branch_and_sha(qtbot, app, monkeypatch):
    """Commit modal should include branch name and short SHA."""
    app.commit_page.commit_message.setPlainText("Snapshot test")
    app.pages.switch_to("commit")  # optional but good UX simulation

    # ✅ Ensure there's something to commit
    test_file = app.project_path / ui_strings.DUMMY_ALS_FILE
    test_file.write_text("test content for snapshot")
    app.repo.git.add(str(test_file))

    captured = {"text": ""}

    def mock_info(_, title, text):
        captured["text"] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "information", mock_info)

    app.commit_changes("Snapshot test")

    # ✅ Validate message contents
    assert "Version Line:" in captured["text"]
    assert "Take ID:" in captured["text"]

    # ✅ Match SHA after "Take ID:"
    match = re.search(r"Take ID:\s*([a-f0-9]{6,})", captured["text"])
    assert match, f"Missing or invalid SHA in: {captured['text']}"


def test_commit_updates_branch_and_commit_labels(qtbot, app):
    """Branch and commit labels should update after commit."""
    app.commit_page.commit_message.setPlainText("Test label update")
    app.pages.switch_to("commit")  # optional but good UX simulation

    # ✅ Ensure there's something to commit
    test_file = app.project_path / ui_strings.DUMMY_ALS_FILE
    test_file.write_text("test content for label update")
    app.repo.git.add(str(test_file))

    app.commit_changes("Test label update")

    assert "Branch:" in app.branch_label.text()
    assert len(app.commit_label.text().split("Commit:")[1].strip()) >= 6


def test_status_label_reflects_commit_after_snapshot(qtbot, app):
    """Status label should include branch and version number after commit."""
    app.commit_page.commit_message.setPlainText("Version update")
    app.pages.switch_to("commit")  # optional but good UX simulation

    # ✅ Ensure there's something to commit
    test_file = app.project_path / ui_strings.DUMMY_ALS_FILE
    test_file.write_text("test content for version update")
    app.repo.git.add(str(test_file))

    app.commit_changes("Version update")

    assert "Version Line" in app.status_label.text()


def test_commit_with_no_changes_shows_error(qtbot, tmp_path):
    app = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(app)
    app.init_git()

    # Add one commit
    f = tmp_path / "session.als"
    f.write_text("init")
    app.repo.git.add("session.als")
    app.repo.index.commit("Initial")

    # ✅ Ensure repo is clean
    # ✅ Auto-remove known tracked/untracked DAWGIT artifacts
    noise_files = [
        ".dawgit_roles.json", ".gitignore", ".dawgit_version_stamp",
        "PROJECT_MARKER.json", "auto_placeholder.als"
    ]
    for noise in noise_files:
        file_path = tmp_path / noise
        if file_path.exists():
            file_path.unlink()

    # ✅ Now check if repo is clean
    assert not app.repo.is_dirty(untracked_files=True), "Repo should be clean after noise cleanup"


    # Reset .dawgit_roles.json if present
    roles_path = tmp_path / ".dawgit_roles.json"
    if roles_path.exists():
        roles_path.unlink()

    # Try committing again with no file changes
    app.commit_page.commit_message.setText("Test Commit")
    app.commit_page.commit_snapshot()

    # ✅ Status label should contain error
    msg = app.commit_page.status_label.text().lower()
    assert "couldn’t save take" in msg or "no changes" in msg
    assert app.commit_page.commit_message.toPlainText() == ""

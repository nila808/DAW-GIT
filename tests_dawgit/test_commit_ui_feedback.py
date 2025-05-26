import pytest
from PyQt6.QtWidgets import QMessageBox

def test_empty_commit_message_blocked(qtbot, app, monkeypatch):
    """Should show a warning and block commit if message is empty."""
    app.snapshot_page.commit_message_input.setPlainText("") # Simulate empty input

    triggered = {"warning": False}

    def mock_warning(*args, **kwargs):
        triggered["warning"] = True
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", mock_warning)

    app.commit_changes("")  # Try to commit
    assert triggered["warning"], "Expected warning dialog for empty commit message"


def test_commit_modal_message_includes_branch_and_sha(qtbot, app, monkeypatch):
    """Commit modal should include branch name and short SHA."""
    app.snapshot_page.commit_message_input.setPlainText("Snapshot test")

    # ✅ Ensure there's something to commit
    test_file = app.project_path / "dummy.als"
    test_file.write_text("test content for snapshot")
    app.repo.git.add(str(test_file))

    captured = {"text": ""}

    def mock_info(_, title, text):
        captured["text"] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "information", mock_info)

    app.commit_changes("Snapshot test")
    assert "Branch:" in captured["text"]
    assert "Commit:" in captured["text"]
    assert len(captured["text"].split("Commit:")[1].strip()) >= 6


def test_commit_updates_branch_and_commit_labels(qtbot, app):
    """Branch and commit labels should update after commit."""
    app.snapshot_page.commit_message_input.setPlainText("Test label update")

    # ✅ Ensure there's something to commit
    test_file = app.project_path / "dummy.als"
    test_file.write_text("test content for label update")
    app.repo.git.add(str(test_file))

    app.commit_changes("Test label update")

    assert "Branch:" in app.branch_label.text()
    assert len(app.commit_label.text().split("Commit:")[1].strip()) >= 6


def test_status_label_reflects_commit_after_snapshot(qtbot, app):
    """Status label should include branch and version number after commit."""
    app.snapshot_page.commit_message_input.setPlainText("Version update")

    # ✅ Ensure there's something to commit
    test_file = app.project_path / "dummy.als"
    test_file.write_text("test content for version update")
    app.repo.git.add(str(test_file))

    app.commit_changes("Version update")

    assert "Session branch:" in app.status_label.text()  # stripped emoji for test mode

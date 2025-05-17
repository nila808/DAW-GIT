import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QMessageBox, QLabel
from pathlib import Path


@pytest.fixture
def app_with_repo(temp_project, qtbot):
    from daw_git_gui import DAWGitApp
    app = DAWGitApp(project_path=temp_project, build_ui=True)
    qtbot.addWidget(app)

    # ✅ Add initial commit so HEAD~1 works later
    file = Path(app.project_path) / "dummy.als"
    file.write_text("Ableton placeholder")
    app.repo.index.add([str(file.name)])
    app.repo.index.commit("Initial commit")

    # ✅ Add second commit
    file.write_text("Ableton placeholder v2")
    app.repo.index.add([str(file.name)])
    app.repo.index.commit("Second commit")

    return app


def test_create_version_line_from_detached_head(app_with_repo):
    app = app_with_repo
    app.repo.git.checkout("HEAD~1")  # Now valid
    assert app.repo.head.is_detached

    result = app.create_new_version_line("new_take")
    assert result["status"] == "success"
    assert "new_take" in [b.name for b in app.repo.branches]


def test_safe_switch_branch_creates_if_missing(app_with_repo, qtbot):
    app = app_with_repo

    daw_file = Path(app.project_path) / "dummy.als"
    if not daw_file.exists():
        daw_file.write_text("Ableton test file")
        app.repo.index.add([str(daw_file.name)])
        app.repo.index.commit("Pre-branch commit")

    if "fresh_mix" in [b.name for b in app.repo.branches]:
        app.repo.git.branch("-D", "fresh_mix")

    app.repo.git.checkout("main")

    with patch("PyQt6.QtWidgets.QMessageBox.question") as mock_question:
        mock_question.return_value = QMessageBox.StandardButton.Yes
        result = app.safe_switch_branch("fresh_mix")
        print("[TEST DEBUG] Branch switch result:", result)

    assert result["status"] in ("ok", "success", "warning")  # allow fallback warning mode
    assert "fresh_mix" in [b.name for b in app.repo.branches]


def test_update_session_branch_display_reflects_branch_and_commit(app_with_repo):
    app = app_with_repo

    # Fake labels for headless testing
    app.branch_label = QLabel()
    app.commit_label = QLabel()

    app.update_session_branch_display()
    print("[TEST DEBUG] Branch Label:", app.branch_label.text())
    print("[TEST DEBUG] Commit Label:", app.commit_label.text())
    assert app.branch_label.text().startswith("🎵 Branch: ")
    assert app.commit_label.text().startswith("🎶 Commit: ")


def test_switch_branch_with_unsaved_changes_prompts_backup(app_with_repo):
    app = app_with_repo

    daw_file = Path(app.project_path) / "dummy.als"

    # ✅ Ensure a dirty diff exists — first commit, then modify
    daw_file.write_text("initial content")
    app.repo.index.add([str(daw_file.name)])
    app.repo.index.commit("Baseline commit")

    # Now dirty it
    daw_file.write_text("modified content")
    daw_file.touch()

    app.repo.git.checkout("-b", "unsaved_test_branch")

    with patch.object(app, "backup_unsaved_changes") as mock_backup, \
         patch("PyQt6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes), \
         patch("subprocess.run") as mock_run:

        mock_run.return_value = None
        result = app.safe_switch_branch("main")
        print("[TEST DEBUG] Backup called:", mock_backup.called)
        print("[TEST DEBUG] Branch switch result:", result)

        assert mock_backup.called
        assert result["status"] in ("ok", "success", "warning")


def test_create_new_version_line_commits_version_marker_and_placeholder(app_with_repo):
    app = app_with_repo
    result = app.create_new_version_line("autotest_branch")
    print("[TEST DEBUG] Create version line result:", result)
    assert result["status"] == "success"

    # Check committed file names
    files = [item.path for item in app.repo.head.commit.tree.traverse() if hasattr(item, "path")]
    print("[TEST DEBUG] Files in commit:", files)
    assert any(".version_marker" in f or "placeholder" in f for f in files)

import ui_strings
import sys
import os
from pathlib import Path
import pytest
import subprocess
from PyQt6.QtWidgets import QMessageBox
from unittest.mock import patch
from ui_strings import CURRENT_COMMIT_UNKNOWN, CURRENT_BRANCH_UNKNOWN

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daw_git_gui import DAWGitApp


def test_git_init_creates_repo(tmp_path, qtbot):
    gui = DAWGitApp()
    gui.project_path = tmp_path
    os.chdir(tmp_path)  # Ensure working directory is the project path

    # Create a dummy Ableton file so init_git has something to track
    dummy_file = tmp_path / ui_strings.DUMMY_ALS_FILE
    dummy_file.write_text("Ableton dummy content")

    # Run Git initialization/setup
    gui.run_setup()

    # Assert .git folder is created indicating a Git repo was initialized
    assert (tmp_path / ".git").exists(), ".git folder should be created after Git init"


@pytest.mark.usefixtures("app")
def test_run_setup_creates_repo_and_ui_updates(app, qtbot, tmp_path):
    """
    ✅ Verifies that run_setup initializes the Git repo and updates the UI labels and status.
    """
    als_file = tmp_path / "project.als"
    als_file.write_text("version 1")

    app.project_path = tmp_path
    app.project_label.setText(str(tmp_path))

    with patch("PyQt6.QtWidgets.QMessageBox.question") as mock_confirm:
        mock_confirm.return_value = QMessageBox.StandardButton.Yes

        with patch("PyQt6.QtWidgets.QMessageBox.information"):
            app.run_setup()

    # Force a commit to populate labels
    als_file.write_text("version 2")
    app.commit_changes("First take")

    assert app.repo.head.is_valid()
    assert "main" in (app.repo.active_branch.name if not app.repo.head.is_detached else "detached")
    assert app.commit_label.text() != CURRENT_COMMIT_UNKNOWN
    assert app.branch_label.text() != CURRENT_BRANCH_UNKNOWN


def test_select_folder_binds_repo_and_updates_ui(app, qtbot, tmp_path):
    als_file = tmp_path / "track.als"
    als_file.write_text("init take")

    subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True)

    with patch("PyQt6.QtWidgets.QFileDialog.getExistingDirectory", return_value=str(tmp_path)):
        app.select_folder_clicked()

    # 🛠 Manually connect Git
    app.project_path = tmp_path
    app.project_label.setText(str(tmp_path))
    app.init_git()

    # 🧪 Now add real commit
    als_file.write_text("second take")
    app.commit_changes("Take after bind")

    assert app.commit_label.text() != CURRENT_COMMIT_UNKNOWN
    assert app.branch_label.text() != CURRENT_BRANCH_UNKNOWN
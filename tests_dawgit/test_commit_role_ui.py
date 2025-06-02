import ui_strings
import pytest
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt  # ✅ Add this
import os
from pathlib import Path

@pytest.fixture
def app(qtbot, tmp_path):
    # Set test environment
    os.environ["DAWGIT_TEST_MODE"] = "1"
    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(tmp_path)

    # Create dummy .als file so the app can commit
    (tmp_path / "test_project.als").write_text("dummy data")

    test_app = DAWGitApp(build_ui=True)
    qtbot.addWidget(test_app)

    # Create an initial commit to work with
    test_app.commit_changes("Initial test commit")
    test_app.update_log()
    return test_app

    def test_main_mix_role_button_updates_ui(qtbot, app):
        if app.history_table.rowCount() == 0:
            pytest.skip("No commits to select")

        last_row = app.history_table.rowCount() - 1
        app.history_table.selectRow(last_row)

        selected_row = app.history_table.currentRow()
        assert selected_row == last_row, "Expected last commit row to be selected"

        # ✅ Force update of current commit ID before tagging
        app._set_commit_id_from_selected_row()
        commit_sha = app.current_commit_id
        assert commit_sha is not None, "❌ current_commit_id should not be None after selecting"

        # 🖱️ Simulate clicking the 'Main Mix' button
        qtbot.mouseClick(app.btn_set_version_main, Qt.MouseButton.LeftButton)

        # 🕒 Wait until the role has been applied
        qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha) == "Main Mix", timeout=2000)

        assert app.btn_set_version_main.isEnabled(), "Main Mix button should be enabled"
        assert app.commit_roles[commit_sha] == "Main Mix", f"Expected 'Main Mix' role on commit {commit_sha}, got: {app.commit_roles.get(commit_sha)}"


    def test_creative_take_role_button_updates_ui(qtbot, app):
        """
        Test that clicking the 'Creative Take' role button assigns the correct role to the latest commit.
        """
        if app.history_table.rowCount() == 0:
            pytest.skip("No commits to select")

        last_row = app.history_table.rowCount() - 1
        app.history_table.selectRow(last_row)

        selected_row = app.history_table.currentRow()
        assert selected_row == last_row, "Expected last commit row to be selected"

        # ✅ Ensure commit SHA is up-to-date before tagging
        app._set_commit_id_from_selected_row()
        commit_sha = app.current_commit_id
        assert commit_sha is not None, "❌ current_commit_id should not be None after selecting"

        # 🖱️ Simulate clicking the 'Creative Take' button
        qtbot.mouseClick(app.btn_set_experiment, Qt.MouseButton.LeftButton)

        # 🕒 Wait until the role has been applied
        qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha) == "Creative Take", timeout=2000)

        commit_role = app.commit_roles.get(commit_sha)
        assert commit_role == "Creative Take", f"Expected 'Creative Take' role on commit {commit_sha}, got: {commit_role}"

import ui_strings
import pytest
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt  # ✅ Add this
import os
from pathlib import Path
from ui_strings import (
    ASSERT_COMMIT_ID_NOT_NONE_MSG,
    ROLE_KEY_ALT_MIXDOWN, 
    ROLE_KEY_MAIN_MIX, 
    ROLE_KEY_CREATIVE_TAKE, 
    ERR_MAIN_MIX_NOT_ASSIGNED, 
    ERR_MAIN_MIX_BUTTON_DISABLED
)


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
    assert commit_sha is not None, ASSERT_COMMIT_ID_NOT_NONE_MSG

    # 🖱️ Simulate clicking the 'ROLE_KEY_MAIN_MIX' button
    qtbot.mouseClick(app.commit_page.tag_main_btn, Qt.MouseButton.LeftButton)

    # 🕒 Wait until the role has been applied
    qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha) == ROLE_KEY_MAIN_MIX, timeout=2000)

    assert app.commit_page.tag_main_btn.isEnabled(), ERR_MAIN_MIX_BUTTON_DISABLED
    assert app.commit_roles[commit_sha] == ROLE_KEY_MAIN_MIX, ERR_MAIN_MIX_NOT_ASSIGNED.format(sha=commit_sha, actual=app.commit_roles.get(commit_sha))



def test_creative_take_role_button_updates_ui(qtbot, app):
    if app.history_table.rowCount() == 0:
        pytest.skip("No commits to select")

    # Select last row (expected to be most recent commit)
    last_row = app.history_table.rowCount() - 1
    app.history_table.selectRow(last_row)
    app._set_commit_id_from_selected_row()
    commit_sha = app.current_commit_id
    assert commit_sha is not None, ASSERT_COMMIT_ID_NOT_NONE_MSG

    # 🖱️ Click 'ROLE_KEY_CREATIVE_TAKE' role button
    qtbot.mouseClick(app.commit_page.tag_alt_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(200)  # Let Qt loop and role assignment complete

    # 🧠 Re-fetch roles to ensure updated state
    assigned = app.commit_roles.get(commit_sha)
    assert assigned == ROLE_KEY_ALT_MIXDOWN, f"Expected {ROLE_KEY_ALT_MIXDOWN}, got {assigned}"




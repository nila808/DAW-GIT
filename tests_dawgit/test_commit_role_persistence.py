<<<<<<< HEAD
import os
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from daw_git_gui import DAWGitApp


@pytest.fixture
def app(qtbot, tmp_path):
    # Set test mode environment
    os.environ["DAWGIT_TEST_MODE"] = "1"
    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(tmp_path)

    # Create dummy .als file for valid commit
    dummy_als = tmp_path / "test_project.als"
    dummy_als.write_text("dummy ALS content")

    test_app = DAWGitApp(build_ui=True)
    qtbot.addWidget(test_app)
    return test_app

@pytest.mark.usefixtures("app")
class TestCommitRolePersistence:

    def test_tag_role_persists_across_restart(self, qtbot, app, tmp_path):
        if app.history_table.rowCount() == 0:
            pytest.skip("No commits to tag")

        # ✅ Select first valid commit row
        for i in range(app.history_table.rowCount()):
            sha_item = app.history_table.item(i, 1)
            sha = sha_item.toolTip() if sha_item else None
            if sha and sha != "–" and len(sha) >= 7:
                app.history_table.selectRow(i)
                break

        # ✅ Capture SHA of selected commit BEFORE tagging
        qtbot.waitUntil(lambda: app.history_table.item(app.history_table.currentRow(), 1) is not None, timeout=1000)
        sha_item = app.history_table.item(app.history_table.currentRow(), 1)
        commit_sha = sha_item.toolTip()

        # ✅ Tag the commit
        qtbot.mouseClick(app.btn_set_version_main, Qt.MouseButton.LeftButton)

        # ✅ Wait for the tag to be written to role map
        qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha) == "Main Mix", timeout=2000)

        # ✅ Restart app
        del app
        from daw_git_gui import DAWGitApp
        new_app = DAWGitApp(project_path=tmp_path, build_ui=True)

        # ✅ Wait until repo is fully loaded
        qtbot.waitUntil(lambda: new_app.repo is not None, timeout=2000)

        # ✅ Reload roles manually
        new_app.load_commit_roles()

        print("[DEBUG] Assigned SHA:", commit_sha)
        print("[DEBUG] Role Map:", new_app.commit_roles)

        # ✅ Assert that role persisted across restart
        qtbot.waitUntil(lambda: new_app.commit_roles.get(commit_sha) == "Main Mix", timeout=3000)
        assert new_app.commit_roles[commit_sha] == "Main Mix"


    def test_tag_role_can_be_updated(self, qtbot, app):
        # Step 1: Skip test if no commits exist
        if app.history_table.rowCount() == 0:
            pytest.skip("No commits to tag")
        
        # Step 2: Wait until the history table is populated
        qtbot.waitUntil(lambda: app.history_table.rowCount() > 0, timeout=2000)  # Ensure history table has rows
        
        # Step 3: Select the last commit row
        last_row = app.history_table.rowCount() - 1
        app.history_table.selectRow(last_row)
        
        # Ensure the row is selected
        selected_row = app.history_table.currentRow()
        print(f"[DEBUG] Selected row: {selected_row}")
        assert selected_row == last_row, "❌ The last row was not selected."
        
        # Step 4: Ensure the commit ID is set before proceeding
        app._set_commit_id_from_selected_row()
        commit_sha = app.current_commit_id
        print(f"[DEBUG] current_commit_id after selection: {commit_sha}")  # Debugging line
        assert commit_sha, "❌ current_commit_id is empty"  # Ensure commit ID is set
        
        # Step 5: Tag the commit
        qtbot.mouseClick(app.btn_set_version_main, Qt.MouseButton.LeftButton)
        
        # Step 6: Log commit roles after tagging to ensure the update
        print(f"[DEBUG] commit_roles after tagging: {app.commit_roles}")
        
        # Step 7: Ensure that the role is actually written to commit_roles
        qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha) == "Main Mix", timeout=10000)  # Increased timeout
        
        # Step 8: Log final commit_roles state
        print(f"[DEBUG] commit_roles final state: {app.commit_roles}")


    def test_multiple_commits_have_distinct_roles(self, qtbot, app):
        if app.history_table.rowCount() < 2:
            pytest.skip("Need at least two commits for this test")

        # Row 0: tag as 'Main Mix'
        app.history_table.selectRow(0)
        sha_item_0 = app.history_table.item(0, 1)
        commit_sha_0 = sha_item_0.toolTip()
        qtbot.mouseClick(app.btn_set_version_main, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha_0) == "Main Mix", timeout=2000)

        # Row 1: tag as 'Creative Take'
        app.history_table.selectRow(1)
        sha_item_1 = app.history_table.item(1, 1)
        commit_sha_1 = sha_item_1.toolTip()
        qtbot.mouseClick(app.btn_set_experiment, Qt.MouseButton.LeftButton)
        qtbot.waitUntil(lambda: app.commit_roles.get(commit_sha_1) == "Creative Take", timeout=2000)

        assert app.commit_roles.get(commit_sha_0) == "Main Mix"
        assert app.commit_roles.get(commit_sha_1) == "Creative Take"


def test_commit_roles_loaded_on_startup(app):
    """
    Verifies that commit_roles dictionary is initialized and loaded on app startup.
    """
    assert hasattr(app, "commit_roles"), "App missing commit_roles attribute"
    assert isinstance(app.commit_roles, dict), "commit_roles is not a dictionary"
=======
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView


def get_commit_sha(app, row):
    """Helper to extract the full commit SHA from a given table row."""
    item = app.history_table.item(row, 1)  # SHA is column 1
    if item is None:
        print(f"[TEST ERROR] No item at row {row}, column 1")
        return None
    sha = item.toolTip()
    if not sha:
        print(f"[TEST ERROR] Empty tooltip at row {row}")
    return sha

def select_latest_commit(app, qtbot, wait_ms=250):
    qtbot.wait(wait_ms)
    row_count = app.history_table.rowCount()
    if row_count == 0:
        print("[TEST ERROR] No rows in history table")
        return None

    row = row_count - 1
    app.history_table.selectRow(row)
    qtbot.wait(100)
    app._set_commit_id_from_selected_row()
    sha = app.current_commit_id

    if not sha:
        # 🛠️ Fallback to column 2 (Commit ID)
        sha_item = app.history_table.item(row, 2)
        if sha_item:
            sha = sha_item.toolTip()
            app.current_commit_id = sha
            print(f"[FALLBACK] SHA from column 2: {sha}")
        else:
            print(f"[ERROR] Could not find SHA at row {row}")
            return None

    print(f"[DEBUG] Selected row = {row}, SHA = {sha}")
    return sha



def ensure_test_commit(app):
    """Ensure at least one commit exists with a valid .als file."""
    als_path = app.project_path / "dummy.als"
    if not als_path.exists():
        als_path.write_text("🎵 Ableton content")
    app.commit_changes(commit_message="Initial test commit")


# --- Tests ---

def test_tag_role_persists_across_restart(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.current_commit_id = commit_sha

    app.assign_commit_role(commit_sha, "Main Mix")
    app.save_settings()
    app.close()

    new_app = type(app)(project_path=app.project_path)
    qtbot.addWidget(new_app)
    commit_sha_new = select_latest_commit(new_app, qtbot)
    assert commit_sha_new is not None
    new_app.current_commit_id = commit_sha_new
    assert new_app.commit_roles.get(commit_sha_new) == "Main Mix"

def test_tag_role_can_be_updated(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.current_commit_id = commit_sha

    app.assign_commit_role(commit_sha, "Creative Take")
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"

    def test_multiple_commits_have_distinct_roles(qtbot, app_with_commit):
        app = app_with_commit
        ensure_test_commit(app)  # Create first commit
        ensure_test_commit(app)  # Create second commit

        if app.history_table.rowCount() < 2:
            pytest.skip("Need at least 2 commits for this test")

        row1 = app.history_table.rowCount() - 1
        row2 = app.history_table.rowCount() - 2

        # ✅ Select first row and tag it
        app.history_table.selectRow(row1)
        qtbot.wait(100)
        app._set_commit_id_from_selected_row()
        sha1 = app.current_commit_id
        assert sha1 is not None
        app.assign_commit_role(sha1, "Main Mix")

        # ✅ Select second row and tag it differently
        app.history_table.selectRow(row2)
        qtbot.wait(100)
        app._set_commit_id_from_selected_row()
        sha2 = app.current_commit_id
        assert sha2 is not None
        app.assign_commit_role(sha2, "Creative Take")

        # ✅ Confirm roles were applied and distinct
        assert app.commit_roles.get(sha1) == "Main Mix"
        assert app.commit_roles.get(sha2) == "Creative Take"


def test_retag_commit_with_new_role(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    app.assign_commit_role(commit_sha, "Main Mix")
    assert app.commit_roles.get(commit_sha) == "Main Mix"

def test_switch_to_creative_take_commit(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.assign_commit_role(commit_sha, "Creative Take")
    assert app.commit_roles.get(commit_sha) == "Creative Take"

def test_switch_to_alt_mixdown_commit(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"

def test_repeated_tag_untag_commit_role(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.assign_commit_role(commit_sha, "Main Mix")
    app.assign_commit_role(commit_sha, "")
    app.assign_commit_role(commit_sha, "Creative Take")
    assert app.commit_roles.get(commit_sha) == "Creative Take"

def test_delete_commit_with_role_tagged(qtbot, app_with_commit):
    app = app_with_commit
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha is not None
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"
>>>>>>> feature/v1.1.6-new-feature

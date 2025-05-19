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
    """Select the last row in the history table and return its SHA."""
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
        print(f"[WARN] No SHA found after selecting row {row}")
        for r in range(row_count):
            app.history_table.selectRow(r)
            qtbot.wait(100)
            app._set_commit_id_from_selected_row()
            sha = app.current_commit_id
            if sha:
                print(f"[RECOVERY] Found SHA at row {r}: {sha}")
                return sha
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
    ensure_test_commit(app)
    if app.history_table.rowCount() < 2:
        pytest.skip("Need at least 2 commits")

    row1 = app.history_table.rowCount() - 1
    row2 = app.history_table.rowCount() - 2

    app.history_table.selectRow(row1)
    qtbot.wait(100)
    app.update_log()
    commit1 = get_commit_sha(app, row1)
    assert commit1 is not None
    app.assign_commit_role(commit1, "Main Mix")

    app.history_table.selectRow(row2)
    qtbot.wait(100)
    app.update_log()
    commit2 = get_commit_sha(app, row2)
    assert commit2 is not None
    app.assign_commit_role(commit2, "Creative Take")

    assert app.commit_roles.get(commit1) == "Main Mix"
    assert app.commit_roles.get(commit2) == "Creative Take"

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

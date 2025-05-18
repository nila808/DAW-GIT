import pytest
from PyQt6.QtCore import Qt

def test_tag_role_persists_across_restart(qtbot, app):
    """
    AT-049 / MT-028 – Assign a commit role and verify it persists across app restart
    """
    if app.history_table.rowCount() == 0:
        pytest.skip("No commits found to tag")

    last_row = app.history_table.rowCount() - 1
    app.history_table.selectRow(last_row)
    app._set_commit_id_from_selected_row()
    commit_sha = app.current_commit_id

    app.assign_commit_role(commit_sha, "Main Mix")
    app.save_settings()
    app.close()

    # Reopen app
    new_app = type(app)(project_path=app.project_path)
    qtbot.addWidget(new_app)
    new_app._set_commit_id_from_selected_row()
    assert new_app.commit_roles.get(commit_sha) == "Main Mix"

def test_tag_role_can_be_updated(qtbot, app):
    """
    AT-050 / MT-029 – Update the role of a previously tagged commit
    """
    if app.history_table.rowCount() == 0:
        pytest.skip("No commits found to tag")

    last_row = app.history_table.rowCount() - 1
    app.history_table.selectRow(last_row)
    app._set_commit_id_from_selected_row()
    commit_sha = app.current_commit_id

    app.assign_commit_role(commit_sha, "Creative Take")
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"

def test_multiple_commits_have_distinct_roles(qtbot, app):
    """
    AT-051 / MT-030 – Tag multiple commits with different roles
    """
    if app.history_table.rowCount() < 2:
        pytest.skip("Need at least 2 commits")

    row1 = app.history_table.rowCount() - 1
    row2 = app.history_table.rowCount() - 2

    app.history_table.selectRow(row1)
    app._set_commit_id_from_selected_row()
    commit1 = app.current_commit_id
    app.assign_commit_role(commit1, "Main Mix")

    app.history_table.selectRow(row2)
    app._set_commit_id_from_selected_row()
    commit2 = app.current_commit_id
    app.assign_commit_role(commit2, "Creative Take")

    assert app.commit_roles.get(commit1) == "Main Mix"
    assert app.commit_roles.get(commit2) == "Creative Take"

# ───────────────────────────────────────────────
# Draft cases from AT-052 to AT-055 – Needs implementation
# ───────────────────────────────────────────────

def test_retag_commit_with_new_role(qtbot, app):
    """AT-052 / MT-031 – Re-tag a commit from one role to another"""
    pass  # TODO: Implement test logic

def test_switch_to_creative_take_commit(qtbot, app):
    """AT-053 / MT-032 – Switch to a commit tagged as Creative Take"""
    pass  # TODO: Implement test logic

def test_switch_to_alt_mixdown_commit(qtbot, app):
    """AT-054 / MT-033 – Switch to a commit tagged as Alt Mixdown"""
    pass  # TODO: Implement test logic

def test_repeated_tag_untag_commit_role(qtbot, app):
    """AT-055 / MT-034 – Tag and untag a commit role repeatedly"""
    pass  # TODO: Implement test logic

def test_delete_commit_with_role_tagged(qtbot, app):
    """AT-056 / MT-035 – Delete a commit that has a role assigned and verify role is removed"""
    pass  # TODO: Implement test logic

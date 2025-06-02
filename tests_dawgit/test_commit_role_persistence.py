import ui_strings
import os
import pytest
from PyQt6.QtCore import Qt
from daw_git_gui import DAWGitApp

# --- Utilities ---

def get_commit_sha(app, row):
    item = app.history_table.item(row, 1)  # SHA is column 1
    return item.toolTip() if item else None

def select_latest_commit(app, qtbot, wait_ms=250):
    qtbot.wait(wait_ms)
    row = app.history_table.rowCount() - 1
    app.history_table.selectRow(row)
    qtbot.wait(100)
    app._set_commit_id_from_selected_row()
    return app.current_commit_id

def ensure_test_commit(app):
    als_path = app.project_path / ui_strings.DUMMY_ALS_FILE
    if not als_path.exists():
        als_path.write_text("🎵 Ableton content")
    app.commit_changes(commit_message="Initial test commit")


# --- Fixtures ---

@pytest.fixture
def app(qtbot, tmp_path):
    os.environ["DAWGIT_TEST_MODE"] = "1"
    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(tmp_path)
    dummy_als = tmp_path / "test_project.als"
    dummy_als.write_text("dummy ALS content")
    test_app = DAWGitApp(build_ui=True)
    qtbot.addWidget(test_app)
    return test_app


# --- Tests ---

def test_tag_role_persists_across_restart(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha

    app.assign_commit_role(commit_sha, "Main Mix")
    app.save_settings()
    app.close()

    new_app = DAWGitApp(project_path=app.project_path, build_ui=True)
    qtbot.addWidget(new_app)
    qtbot.waitUntil(lambda: new_app.repo is not None, timeout=2000)
    new_app.load_commit_roles()

    assert new_app.commit_roles.get(commit_sha) == "Main Mix"


def test_tag_role_can_be_updated(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha

    app.assign_commit_role(commit_sha, "Creative Take")
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"


def test_multiple_commits_have_distinct_roles(qtbot, app):
    ensure_test_commit(app)
    ensure_test_commit(app)

    if app.history_table.rowCount() < 2:
        pytest.skip("Need at least two commits for this test")

    # Tag commit 0 as Main Mix
    app.history_table.selectRow(0)
    qtbot.wait(100)
    app._set_commit_id_from_selected_row()
    sha1 = app.current_commit_id
    app.assign_commit_role(sha1, "Main Mix")

    # Tag commit 1 as Creative Take
    app.history_table.selectRow(1)
    qtbot.wait(100)
    app._set_commit_id_from_selected_row()
    sha2 = app.current_commit_id
    app.assign_commit_role(sha2, "Creative Take")

    assert app.commit_roles.get(sha1) == "Main Mix"
    assert app.commit_roles.get(sha2) == "Creative Take"


def test_retag_commit_with_new_role(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    app.assign_commit_role(commit_sha, "Main Mix")
    assert app.commit_roles.get(commit_sha) == "Main Mix"


def test_switch_to_creative_take_commit(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha
    app.assign_commit_role(commit_sha, "Creative Take")
    assert app.commit_roles.get(commit_sha) == "Creative Take"


def test_switch_to_alt_mixdown_commit(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"


def test_repeated_tag_untag_commit_role(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha
    app.assign_commit_role(commit_sha, "Main Mix")
    app.assign_commit_role(commit_sha, "")
    app.assign_commit_role(commit_sha, "Creative Take")
    assert app.commit_roles.get(commit_sha) == "Creative Take"


def test_delete_commit_with_role_tagged(qtbot, app):
    ensure_test_commit(app)
    commit_sha = select_latest_commit(app, qtbot)
    assert commit_sha
    app.assign_commit_role(commit_sha, "Alt Mixdown")
    assert app.commit_roles.get(commit_sha) == "Alt Mixdown"


def test_commit_roles_loaded_on_startup(app):
    assert hasattr(app, "commit_roles")
    assert isinstance(app.commit_roles, dict)

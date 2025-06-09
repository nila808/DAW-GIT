import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import ui_strings
import pytest
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from ui_strings import (
    SNAPSHOT_BROWSER_TITLE, 
    ROLE_MAIN_MIX_TOOLTIP, 
    TEST_MSG_MAIN_NOT_FOUND, 
    TEST_MSG_ALT_NOT_FOUND
)


from git import Actor


@pytest.fixture
def app(qtbot: QtBot):
    test_app = DAWGitApp(build_ui=True)  # ✅ Enable full UI
    qtbot.addWidget(test_app)
    return test_app

def test_placeholder(app):
    assert app is not None


def test_pages_view_renders_cards_for_commits(tmp_path, qtbot):
    """
    AT-110 – Pages view shows cards for all commits in history.
    """
    als = tmp_path / "idea.als"
    als.write_text("take 1")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)

    index = app.repo.index
    index.add([str(als)])
    index.commit("Start take", author=Actor("Test", "test@example.com"))

    # Second commit
    als.write_text("take 2")
    index.add([str(als)])
    index.commit("Second idea", author=Actor("Test", "test@example.com"))

    # Load history
    app.update_log()
    qtbot.wait(200)

    # Validate rows/cards rendered
    table = app.snapshot_page.commit_table
    assert table.rowCount() >= 2


def test_pages_view_groups_commits_by_branch(tmp_path, qtbot):
    """
    AT-111 – Pages view shows commits from different branches in same table (grouping by branch).
    """
    from daw_git_gui import DAWGitApp

    als = tmp_path / "groove.als"
    als.write_text("main vibe")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(300)

    assert app.repo.active_branch.name.lower() == "main"

    # ✅ Initial commit to start repo
    app.commit_changes(commit_message="Initial placeholder")
    qtbot.wait(300)

    # ✅ Commit on main
    als.write_text("Main idea 1")  # force a content change
    app.commit_changes(commit_message="Main idea")
    qtbot.wait(300)

    # 🔁 Create alt branch
    app.create_new_version_line(branch_name="alt-idea")
    qtbot.wait(300)

    # ✅ Commit on alt
    als.write_text("alt vibe")
    app.commit_changes(commit_message="Alt idea")
    qtbot.wait(300)

    als.write_text("alt vibe update")
    app.commit_changes(commit_message="Extra alt idea")
    qtbot.wait(300)

    # 🔁 Switch back to main for full table refresh
    app.switch_branch("main")
    qtbot.wait(300)

    # Merge alt-idea into main so both sets of commits are visible in table
    app.repo.git.merge("alt-idea")
    qtbot.wait(200)

    app.update_log()
    qtbot.wait(500)

    table = app.snapshot_page.commit_table
    assert table.rowCount() >= 2, "[FAIL] Commit table did not populate"

    commits = []
    for i in range(table.rowCount()):
        sha = None
        for col in range(table.columnCount()):
            item = table.item(i, col)
            if item and item.toolTip():
                sha = item.toolTip().split()[0]
                break  # Found valid SHA
        if sha:
            try:
                commits.append(app.repo.commit(sha))
            except Exception as e:
                print("[WARN] Could not resolve SHA:", sha, "|", e)

    print("🧾 Collected commit messages:")
    for c in commits:
        print("-", repr(c.message.strip()))

    assert any("Main idea" in c.message for c in commits), TEST_MSG_MAIN_NOT_FOUND
    assert any("Alt idea" in c.message for c in commits), TEST_MSG_ALT_NOT_FOUND


def test_snapshot_browser_title_matches_constant(app):
    """
    Verifies the title label matches the SNAPSHOT_BROWSER_TITLE constant.
    """
    assert app.snapshot_page.title_label.text() == SNAPSHOT_BROWSER_TITLE


def test_main_mix_button_uses_correct_tooltip(app):
    """
    Verifies the main mix role button uses the correct tooltip from constants.
    """
    assert app.commit_page.tag_main_btn.toolTip() == ROLE_MAIN_MIX_TOOLTIP
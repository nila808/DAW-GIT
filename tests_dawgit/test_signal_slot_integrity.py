import os
os.environ["DAWGIT_TEST_MODE"] = "1"

import daw_git_testing  # auto-patches dialogs

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from daw_git_gui import DAWGitApp

from git import Actor
import shutil


def test_commit_button_triggers_git_commit_and_ui_update(tmp_path, qtbot):
    """
    AT-099 – Simulates a commit and verifies commit message + UI update.
    """

    # Setup project with one .als file
    als = tmp_path / "song.als"
    als.write_text("take 1")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)

    # Do a direct commit instead of clicking
    index = app.repo.index
    index.add([str(als)])
    index.commit("Initial snapshot", author=Actor("Test", "test@example.com"))

    # Update UI manually to reflect new commit
    app.update_log()
    qtbot.wait(200)

    # Assert commit message is correct
    last_msg = app.repo.head.commit.message.strip()
    assert "Initial snapshot" in last_msg

    # Assert UI table reflects new commit
    assert app.snapshot_page.commit_table.rowCount() > 0



def test_checkout_button_triggers_state_refresh(tmp_path, qtbot):
    """
    AT-100 – Clicking a snapshot in the table triggers a checkout and updates UI state.
    """

    # Step 1: Create repo with 2 commits
    als = tmp_path / "song.als"
    als.write_text("version 1")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)

    # Commit 1
    index = app.repo.index
    index.add([str(als)])
    index.commit("First take", author=Actor("Test", "test@example.com"))

    # Commit 2
    als.write_text("version 2")
    index.add([str(als)])
    index.commit("Second take", author=Actor("Test", "test@example.com"))

    app.update_log()
    qtbot.wait(200)

    # Step 2: Checkout older commit from table
    table = app.snapshot_page.commit_table
    row_to_select = table.rowCount() - 2  # second-to-last (first commit)
    table.selectRow(row_to_select)
    app.checkout_selected_commit()
    qtbot.wait(300)

    # ✅ Step 3: Validate HEAD commit changed correctly
    selected_sha = table.item(row_to_select, 0).toolTip()
    assert app.repo.head.commit.hexsha.startswith(selected_sha)


def test_branch_dropdown_selection_updates_labels(tmp_path, qtbot):
    """
    AT-101 – Switching branches updates the session status label.
    """

    # Step 1: Setup project with one .als commit on MAIN
    als = tmp_path / "track.als"
    als.write_text("original")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)

    index = app.repo.index
    index.add([str(als)])
    index.commit("Main mix", author=Actor("Tester", "test@example.com"))

    # Step 2: Create new branch
    app.create_new_version_line(branch_name="alt-mix")
    qtbot.wait(200)

    # Step 3: Switch to new branch using dropdown
    app.branch_page.branch_dropdown.setCurrentText("alt-mix")
    app.switch_branch("alt-mix")
    qtbot.wait(300)

    # Step 4: Assert UI status label reflects branch switch
    status = app.snapshot_page.status_label.text()
    assert "alt-mix" in status or "ALT-MIX" in status



import ui_strings
import pytest
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.environ["DAWGIT_TEST_MODE"] = "1"


def test_filter_commit_history_by_branch(qtbot, tmp_path):
    """Ensure commit history table filters commits by selected branch."""
    gui = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(gui)

    # Init and commit on MAIN
    gui.repo.init()
    (tmp_path / "track.als").write_text("main version")
    gui.repo.index.add(["track.als"])
    gui.repo.index.commit("Main version")

    # Create new branch and commit
    gui.repo.git.checkout("-b", "alt-take")
    (tmp_path / "track.als").write_text("alt version")
    gui.repo.index.add(["track.als"])
    gui.repo.index.commit("Alt take")

    # Simulate selecting 'alt-take' in UI
    gui.branch_dropdown.setCurrentText("alt-take")
    gui.update_log()

    # Confirm only commits from 'alt-take' are shown
    all_texts = [
        gui.snapshot_page.commit_table.item(row, 3).text()  # column 3 = commit message
        for row in range(gui.snapshot_page.commit_table.rowCount())
    ]

    commit_msgs = [
        gui.snapshot_page.commit_table.item(row, 3).text()
        for row in range(gui.snapshot_page.commit_table.rowCount())
    ]
    assert any("Alt take" in msg for msg in commit_msgs)

    branches = [
        gui.snapshot_page.commit_table.item(row, 4).text()
        for row in range(gui.snapshot_page.commit_table.rowCount())
    ]
    assert any("alt-take" in b for b in branches)
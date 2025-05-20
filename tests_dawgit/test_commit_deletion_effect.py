import os
import subprocess
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox

from daw_git_gui import DAWGitApp
from git import Repo


@pytest.fixture
def repo_with_multiple_commits(tmp_path):
    project_dir = tmp_path / "DeleteCommitTest"
    project_dir.mkdir()

    file1 = project_dir / "a.als"
    file2 = project_dir / "b.als"
    file1.write_text("First version")
    file2.write_text("Second version")

    # Init and commit directly
    repo = Repo.init(project_dir)
    repo.index.add(["a.als", "b.als"])
    repo.index.commit("Commit A + B")

    app = DAWGitApp(project_path=project_dir, build_ui=False)
    app.init_git()

    return app


def test_deleted_commit_disappears_from_history(qtbot, repo_with_multiple_commits, monkeypatch):
    app = repo_with_multiple_commits
    project_dir = app.project_path
    repo = app.repo


    # Create second commit to delete
    second_file = project_dir / "b.als"
    second_file.write_text("another session")
    repo.index.add([str(second_file.relative_to(project_dir))])
    repo.index.commit("Second commit")

    # ✅ Launch app
    app = DAWGitApp(project_path=project_dir, build_ui=False)
    app.init_git()
    qtbot.addWidget(app)

    # ✅ Populate mock history_table (1 row = 2nd commit)
    commit_sha = repo.head.commit.hexsha
    commit_msg = repo.head.commit.message.strip()
    app.history_table = QTableWidget(1, 3)
    item_sha = QTableWidgetItem(commit_sha[:7])
    item_sha.setToolTip(commit_sha)
    item_msg = QTableWidgetItem(commit_msg)
    app.history_table.setItem(0, 1, item_sha)
    app.history_table.setItem(0, 2, item_msg)
    app.history_table.selectRow(0)

    app.current_commit_id = commit_sha

    # ✅ Monkeypatch delete confirmation
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    # ✅ Delete commit
    app.delete_selected_commit()

    # ✅ Confirm commit no longer in Git log
    remaining_commits = [c.hexsha for c in repo.iter_commits()]
    assert commit_sha not in remaining_commits, "Commit still exists in Git history"

    # ✅ Confirm commit no longer in UI table
    for row in range(app.history_table.rowCount()):
        tooltip = app.history_table.item(row, 1).toolTip()
        assert tooltip != commit_sha, "Commit still displayed in UI table"

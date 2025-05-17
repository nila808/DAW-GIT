import os
import subprocess
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox

from daw_git_gui import DAWGitApp
from git import Repo


@pytest.fixture
def repo_with_multiple_commits(tmp_path):
    """Creates a repo with two committed .als files."""
    project_dir = tmp_path / "DeleteCommitTest"
    project_dir.mkdir()

    file1 = project_dir / "a.als"
    file2 = project_dir / "b.als"
    file1.write_text("First version")
    file2.write_text("Second version")

    app = DAWGitApp(project_path=project_dir, build_ui=False)
    app.init_git()

    # ✅ Use relative paths *from project_dir* for git add
    app.repo.index.add([str(file1.relative_to(project_dir))])
    app.repo.index.commit("First commit")
    app.repo.index.add([str(file2.relative_to(project_dir))])
    app.repo.index.commit("Second commit")

    return app


def test_deleted_commit_disappears_from_history(repo_with_multiple_commits):
    app = repo_with_multiple_commits

    initial_commits = list(app.repo.iter_commits("HEAD"))
    assert len(initial_commits) >= 2

    target_commit = initial_commits[-2]  # ✅ Non-root, safe to delete
    target_sha = target_commit.hexsha

    # 🔁 Simulate user selection in UI
    app.history_table = QTableWidget(1, 3)
    item_sha = QTableWidgetItem(target_sha[:7])
    item_sha.setToolTip(target_sha)
    item_msg = QTableWidgetItem(target_commit.message.strip())
    app.history_table.setItem(0, 1, item_sha)
    app.history_table.setItem(0, 2, item_msg)
    app.history_table.selectRow(0)

    # 🧪 Simulate confirmation
    QMessageBox.question = lambda *a, **k: QMessageBox.StandardButton.Yes

    # 🧨 Delete via app logic (not raw Git)
    app.delete_selected_commit()

    # 🔍 Confirm commit is gone
    updated_commits = list(app.repo.iter_commits("HEAD"))
    updated_shas = [c.hexsha for c in updated_commits]

    assert target_sha not in updated_shas, "Deleted commit should no longer be in history"

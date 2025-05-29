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

    repo = Repo.init(project_dir)
    repo.index.add(["a.als", "b.als"])
    repo.index.commit("Commit A + B")

    return project_dir, repo


def test_deleted_commit_disappears_from_history(qtbot, repo_with_multiple_commits, monkeypatch):
    project_dir, repo = repo_with_multiple_commits

    # Add second commit to delete
    second_file = project_dir / "b.als"
    second_file.write_text("another session")
    repo.index.add(["b.als"])
    repo.index.commit("Second commit")

    commit_sha = repo.head.commit.hexsha

    # Launch app with full UI
    app = DAWGitApp(project_path=project_dir, build_ui=True)
    app.init_git()
    qtbot.addWidget(app)

    # Simulate UI selection state
    app.current_commit_id = commit_sha
    app.load_commit_history()

    # Confirm dialog auto-accept
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    # Delete the commit
    app.delete_selected_commit()

    # Rebuild commit list post-delete
    app.load_commit_history()

    # Validate it's gone from Git
    remaining_shas = [c.hexsha for c in repo.iter_commits()]
    assert commit_sha not in remaining_shas, "Commit still exists in Git history"

    # Validate it's gone from UI
    table = app.snapshot_page.commit_table
    for row in range(table.rowCount()):
        tooltip = table.item(row, 2).toolTip()  # Column 2 = SHA
        assert tooltip != commit_sha, "Commit still displayed in UI table"
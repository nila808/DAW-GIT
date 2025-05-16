import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox

@pytest.fixture
def repo_with_commits(tmp_path):
    """Set up a repo with at least one commit."""
    project_dir = tmp_path / "DeleteCommitRepo"
    project_dir.mkdir()
    file = project_dir / "file.als"
    file.write_text("Initial content")

    repo = Repo.init(str(project_dir))
    repo.index.add([str(file.relative_to(project_dir))])
    repo.index.commit("Initial commit")
    return project_dir, repo

def test_delete_commit(qtbot, repo_with_commits, monkeypatch):
    project_dir, repo = repo_with_commits
    app = DAWGitApp(project_path=project_dir, build_ui=False)
    app.repo = repo
    qtbot.addWidget(app)

    # Populate history_table with one commit
    app.history_table = QTableWidget(1, 3)
    commit_sha = repo.head.commit.hexsha
    commit_msg = repo.head.commit.message.strip()

    item_sha = QTableWidgetItem(commit_sha[:7])
    item_sha.setToolTip(commit_sha)
    item_msg = QTableWidgetItem(commit_msg)

    # Assuming col 1 = SHA, col 2 = message
    app.history_table.setItem(0, 1, item_sha)
    app.history_table.setItem(0, 2, item_msg)
    app.history_table.selectRow(0)

    # Auto-confirm delete dialog
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    # Call the deletion method
    app.delete_selected_commit()

    # Refresh commits list after deletion
    commits_after = list(app.repo.iter_commits())

    # Assert the deleted commit SHA no longer exists
    assert commit_sha not in [c.hexsha for c in commits_after], "Commit was not deleted"

import ui_strings
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
    repo.index.commit(ui_strings.INITIAL_COMMIT_MESSAGE)

    # Create a second commit so we aren't deleting the root commit
    second_file = project_dir / "second.als"
    second_file.write_text("more content")
    repo.index.add([str(second_file.relative_to(project_dir))])
    repo.index.commit("Second commit")

    return project_dir, repo


def test_delete_commit(qtbot, repo_with_commits, monkeypatch):
    project_dir, repo = repo_with_commits

    app = DAWGitApp(project_path=project_dir, build_ui=False)  # ✅ Initialize first
    app.repo = repo
    app.init_git()
    qtbot.addWidget(app)

    # Create a second commit so we're not deleting the root
    second_file = project_dir / "second.als"
    second_file.write_text("more content")
    repo.index.add([str(second_file.relative_to(project_dir))])
    repo.index.commit("Second commit")

    # Target the latest commit (second one)
    commit_sha = repo.head.commit.hexsha
    commit_msg = repo.head.commit.message.strip()

    # Populate table with that commit
    app.history_table = QTableWidget(1, 3)
    item_sha = QTableWidgetItem(commit_sha[:7])
    item_sha.setToolTip(commit_sha)
    item_msg = QTableWidgetItem(commit_msg)
    app.history_table.setItem(0, 1, item_sha)
    app.history_table.setItem(0, 2, item_msg)
    app.history_table.selectRow(0)

    # ✅ Set commit ID manually (normally done by UI callback)
    app.current_commit_id = commit_sha

    # Auto-confirm delete dialog
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    # Perform deletion
    app.delete_selected_commit()

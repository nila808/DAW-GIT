import ui_strings
import os
import pytest
from git import Repo
from pathlib import Path
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import



@pytest.fixture
def repo_with_commits(tmp_path):
    repo_dir = tmp_path / "TestProject"
    repo_dir.mkdir()

    # Simulate two commits
    repo = Repo.init(repo_dir)
    file1 = repo_dir / "file1.als"
    file1.write_text("First version")
    repo.git.add(".")
    repo.index.commit("Commit 1")

    file2 = repo_dir / "file2.als"
    file2.write_text("Second version")
    repo.git.add(".")
    repo.index.commit("Commit 2")

    return repo

def test_return_to_latest_from_detached_head(qtbot, tmp_path, repo_with_commits):
    from daw_git_gui import DAWGitApp
    repo = repo_with_commits

    # Simulate checkout to an earlier commit (detached HEAD)
    older_commit = next(repo.iter_commits('HEAD~1', max_count=1))
    repo.git.checkout(older_commit.hexsha)
    assert repo.head.is_detached

    app = DAWGitApp(project_path=repo.working_tree_dir, build_ui=True)
    qtbot.addWidget(app)

    # Call the return method
    app.return_to_latest_clicked()

    # Check we are back on 'main'
    assert not repo.head.is_detached
    assert repo.active_branch.name == "main"
    assert app.repo.active_branch.name == "main"

import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path
import subprocess

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

    # Commit first file
    app.repo.index.add([file1.name])
    app.repo.index.commit("First snapshot")

    # Commit second file
    app.repo.index.add([file2.name])
    app.repo.index.commit("Second snapshot")

    return app

def test_deleted_commit_disappears_from_history(repo_with_multiple_commits):
    app = repo_with_multiple_commits

    initial_commits = list(app.repo.iter_commits("HEAD"))
    assert len(initial_commits) >= 2

    target_commit = initial_commits[0]  # Oldest commit
    target_sha = target_commit.hexsha

    # Rebase to drop oldest commit
    base = initial_commits[1]
    subprocess.run(
        ["git", "rebase", "--onto", base.hexsha, target_sha],
        cwd=app.project_path,
        env=app.custom_env(),
        check=True
    )

    remaining_commits = list(app.repo.iter_commits("HEAD"))
    remaining_shas = [c.hexsha for c in remaining_commits]

    assert target_sha not in remaining_shas, "Deleted commit should no longer be in history"

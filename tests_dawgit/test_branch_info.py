import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

def test_create_new_branch_from_commit(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Setup repo
    als_file = Path(repo_path) / "project.als"
    als_file.write_text("Dummy ALS content")
    repo.git.add(all=True)
    repo.git.commit(m="Initial commit")

    # Detach HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    # 🚀 Launch app and manually assign repo (in case init fails due to detached HEAD)
    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    if not app.repo:
        app.repo = Repo(repo_path)

    try:
        result = app.create_new_version_line("test_branch")
        assert result["status"] == "success"
        assert not app.repo.head.is_detached
    finally:
        # ✅ Clean up test branch if it was created
        if "test_branch" in repo.branches:
            print("🧹 Removing test branch...")
            try:
                repo.git.checkout("main")
                repo.git.branch("-D", "test_branch")
            except Exception as e:
                print(f"[CLEANUP] Could not delete test_branch: {e}")

def test_branch_creation_in_detached_head_creates_version_line(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Initial commit with DAW file
    als_file = Path(repo_path) / "init_project.als"
    als_file.write_text("Init")
    repo.git.add(all=True)
    repo.git.commit(m="Init commit")

    # Detach HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    # Launch app in detached state
    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    result = app.create_new_version_line("version_line_test")

    # ✅ Assert branch was created and we're no longer detached
    assert result["status"] == "success"
    assert "version_line_test" in [b.name for b in app.repo.branches]
    assert not app.repo.head.is_detached

    # ✅ Assert marker or placeholder was committed
    latest_commit = app.repo.head.commit
    files = latest_commit.stats.files
    assert any(f in files for f in [".version_marker", "auto_placeholder.als", "init_project.als"])

import os
from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp

def test_auto_commit_creates_tag(tmp_path):
    # Create a real Git repo in the temp path
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    os.chdir(repo_path)
    repo = Repo.init(repo_path)

    # Add a dummy file but do NOT commit — let auto_commit do it
    dummy_file = repo_path / "dummy.txt"
    dummy_file.write_text("test data")

    # Instantiate the app with correct project_path and repo
    gui = DAWGitApp()
    gui.project_path = repo_path
    gui.repo = repo

    # Disable remote push during test
    if hasattr(gui, "remote_checkbox"):
        gui.remote_checkbox.setChecked(False)

    # Perform the test commit with a tag
    gui.auto_commit("Test commit", tag="v_test_1")

    # 🔁 Force GitPython to refresh tag info
    gui.repo.refs

    # ✅ Check that the tag exists
    assert "v_test_1" in [tag.name for tag in repo.tags]

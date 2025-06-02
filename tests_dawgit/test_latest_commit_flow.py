import ui_strings
import os
import shutil
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

def test_commit_and_return_to_latest(tmp_path, qtbot):
    # Setup: create a fake project directory
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir()
    als_file = project_path / ui_strings.DUMMY_ALS_FILE
    als_file.write_text("test content")

    # Init Git repo manually
    repo = Repo.init(project_path)

    # Safely handle working directory
    try:
        cwd = os.getcwd()
    except FileNotFoundError:
        cwd = "/tmp"

    os.chdir(project_path)  # switch into valid Git repo before GitPython operations
    try:
        repo.index.add([ui_strings.DUMMY_ALS_FILE])
        repo.index.commit("Initial dummy")
    finally:
        os.chdir(cwd)

    repo.git.branch("-M", "main")  # Rename to main

    # Launch app
    app = DAWGitApp(project_path=project_path, build_ui=True)
    app.custom_env = lambda: {}  # no-op for testing
    app.repo = repo

    # Make second commit
    als_file.write_text("new content")
    app.commit_changes(commit_message="Added update")
    new_sha = app.repo.head.commit.hexsha

    # Checkout the initial commit (detached HEAD)
    first_sha = list(app.repo.iter_commits("main"))[-1].hexsha
    app.checkout_selected_commit(commit_sha=first_sha)
    assert app.repo.head.is_detached
    assert app.repo.head.commit.hexsha == first_sha

    # Return to latest commit
    app.return_to_latest_clicked()

    # Reload repo object after subprocess calls
    app.repo = Repo(project_path)

    # Assertions — ensure you're back on main and HEAD is updated
    assert not app.repo.head.is_detached
    assert app.repo.active_branch.name == "main"
    assert app.repo.head.commit.hexsha == new_sha

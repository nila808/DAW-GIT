import shutil
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

def test_commit_and_return_to_latest(tmp_path, qtbot):
    # Setup: create a fake project directory
    project_path = tmp_path / "TestProject"
    project_path.mkdir()
    als_file = project_path / "dummy.als"
    als_file.write_text("test content")

    # Init Git repo manually
    repo = Repo.init(project_path)
    repo.index.add(["dummy.als"])
    repo.index.commit("Initial commit")
    repo.git.branch("-M", "main")  # Rename to main

    # Launch app
    app = DAWGitApp(project_path=project_path, build_ui=False)
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

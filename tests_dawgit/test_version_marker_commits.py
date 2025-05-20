import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path
import subprocess

@pytest.fixture
def empty_daw_project(tmp_path):
    """Creates an empty project folder with no .als/.logicx files."""
    project_dir = tmp_path / "VersionMarkerTest"
    project_dir.mkdir()
    return project_dir

def test_version_marker_commit_creates_file_and_commit(tmp_path):
    """
    AT-042 – Starting a version line should create and commit a .version_marker file.
    """
    from git import Repo
    from daw_git_gui import DAWGitApp

    # Step 1: Create Git repo with 1 committed .als file
    repo = Repo.init(tmp_path)
    als_file = tmp_path / "main.als"
    als_file.write_text("Ableton baseline")
    repo.index.add(["main.als"])
    repo.index.commit("Initial project")

    # Step 2: Detach HEAD to simulate snapshot mode
    repo.git.checkout(repo.head.commit.hexsha)
    assert repo.head.is_detached

    # Step 3: Launch app and remove .als so placeholder is needed
    als_file.unlink()
    app = DAWGitApp(project_path=tmp_path, build_ui=False)
    app.init_git()

    # Step 4: Start version line
    result = app.create_new_version_line("marker_test_branch")

    # Step 5: Confirm success
    assert result["status"] == "success"

    # Step 6: Check .version_marker file exists
    version_marker = tmp_path / ".version_marker"
    assert version_marker.exists(), ".version_marker file not created"

    # Step 7: Check it was committed
    last_commit = repo.head.commit
    committed_files = last_commit.stats.files
    assert ".version_marker" in committed_files, ".version_marker not committed"

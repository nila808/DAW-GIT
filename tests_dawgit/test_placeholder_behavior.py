import os
import pytest
from git import Repo
from daw_git_gui import DAWGitApp
from pathlib import Path

@pytest.fixture
def project_without_daw_files(tmp_path):
    """Creates a clean project folder with no .als or .logicx files."""
    project_dir = tmp_path / "PlaceholderTest"
    project_dir.mkdir()
    return project_dir

def test_placeholder_file_created_on_version_line_start(tmp_path):
    """
    AT-041 – Starting a new version line from a detached commit should create and commit a placeholder .als file.
    """
    from daw_git_gui import DAWGitApp

    # Step 1: Setup a Git repo with a committed .als
    repo = Repo.init(tmp_path)
    als_file = tmp_path / "base.als"
    als_file.write_text("Initial Ableton session")
    repo.index.add(["base.als"])
    repo.index.commit("Initial commit")

    # Step 2: Detach HEAD (simulate user viewing old snapshot)
    repo.git.checkout(repo.head.commit.hexsha)
    assert repo.head.is_detached

    # Step 3: Launch app and initialize
    app = DAWGitApp(project_path=tmp_path, build_ui=False)
    app.init_git()

    als_file.unlink()  # Remove base.als to trigger placeholder creation

    # Step 4: Start a new version line
    result = app.create_new_version_line("new_version_test")

    # Step 5: Check result is successful
    assert result["status"] == "success", "Expected success creating new version line with placeholder"
    assert result["branch"] == "new_version_test"

    # Step 6: Check for placeholder .als file
    placeholder_file = tmp_path / "auto_placeholder.als"
    assert placeholder_file.exists(), "Placeholder .als file not found"

    # Step 7: Confirm it was committed
    latest_commit = repo.head.commit
    committed_files = latest_commit.stats.files.keys()
    assert "auto_placeholder.als" in committed_files, "Placeholder file was not committed"

def test_placeholder_file_committed_to_repo(project_without_daw_files):
    os.environ["DAWGIT_FORCE_TEST_PATH"] = str(project_without_daw_files)

    app = DAWGitApp(project_path=project_without_daw_files, build_ui=False)
    app.init_git()
    app.create_new_version_line("with-placeholder")

    # Check if placeholder file is tracked in Git index
    tracked_files = list(app.repo.git.ls_files().splitlines())
    assert "auto_placeholder.als" in tracked_files, "Placeholder should be committed"

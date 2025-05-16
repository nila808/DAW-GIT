import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path

@pytest.fixture
def project_without_daw_files(tmp_path):
    """Creates a clean project folder with no .als or .logicx files."""
    project_dir = tmp_path / "PlaceholderTest"
    project_dir.mkdir()
    return project_dir

def test_placeholder_file_created_on_version_line_start(qtbot, project_without_daw_files):
    app = DAWGitApp(project_path=project_without_daw_files, build_ui=False)
    app.init_git()
    result = app.create_new_version_line("v1-experiment")

    placeholder_path = project_without_daw_files / "auto_placeholder.als"
    assert placeholder_path.exists(), "auto_placeholder.als should be created"

    assert result["status"] == "success"
    assert "🎼" in result["commit_message"]

def test_placeholder_file_committed_to_repo(project_without_daw_files):
    app = DAWGitApp(project_path=project_without_daw_files, build_ui=False)
    app.init_git()
    app.create_new_version_line("with-placeholder")

    tracked_files = list(app.repo.git.ls_files().splitlines())
    assert "auto_placeholder.als" in tracked_files, "Placeholder should be committed"

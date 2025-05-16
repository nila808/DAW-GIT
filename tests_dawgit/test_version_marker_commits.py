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

def test_version_marker_commit_creates_file_and_commit(qtbot, empty_daw_project):
    # ✅ Create a dummy .als file so project is valid
    dummy_als = empty_daw_project / "dummy.als"
    dummy_als.write_text("Ableton placeholder")

    app = DAWGitApp(project_path=empty_daw_project, build_ui=False)
    qtbot.addWidget(app)

    app.init_git()

    result = app.create_new_version_line("version_marker_test")

    # ✅ Assert overall result is success and includes commit message
    assert result["status"] == "success"
    assert "commit_message" in result
    assert "🎼" in result["commit_message"]

    # ✅ Assert version marker file was created and committed
    marker_file = empty_daw_project / ".version_marker"
    assert marker_file.exists(), ".version_marker file should be created"

    # ✅ Confirm it's in Git
    committed_files = app.repo.git.ls_files().splitlines()
    assert ".version_marker" in committed_files, ".version_marker should be tracked in Git"

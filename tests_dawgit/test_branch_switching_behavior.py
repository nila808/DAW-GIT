import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import
import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path

@pytest.fixture
def simple_daw_repo(tmp_path):
    """
    Creates a simple Git repo with one commit on the main branch.
    """
    project_dir = tmp_path / "BranchSwitchTest"
    project_dir.mkdir()
    (project_dir / "test.als").write_text("Ableton baseline")

    app = DAWGitApp(project_path=project_dir, build_ui=False)
    app.init_git()  # Initializes Git repo and commits the .als file

    return app

def test_switching_to_same_branch_does_nothing(simple_daw_repo):
    app = simple_daw_repo
    current_branch = app.repo.active_branch.name

    result = app.switch_branch(current_branch)
    
    # The switch_branch method may return 'success' if no switch needed, or 'cancelled' if user cancels.
    assert result["status"] in ("success", "cancelled"), "Switching to current branch should succeed or be cancelled gracefully"
    assert app.repo.active_branch.name == current_branch, "Should remain on the same branch"

import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path

@pytest.fixture
def simple_daw_repo(tmp_path):
    """Creates a repo with a single branch and a commit."""
    project_dir = tmp_path / "BranchSwitchTest"
    project_dir.mkdir()
    (project_dir / "test.als").write_text("Ableton baseline")

    app = DAWGitApp(project_path=project_dir, build_ui=False)
    app.init_git()

    return app

def test_switching_to_same_branch_does_nothing(simple_daw_repo):
    app = simple_daw_repo
    current_branch = app.repo.active_branch.name

    result = app.switch_branch(current_branch)
    
    assert result["status"] == "success" or result["status"] == "cancelled"
    assert app.repo.active_branch.name == current_branch, "Should remain on the same branch"

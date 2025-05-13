
import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp, Repo, QTestAppWrapper

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_create_new_branch_from_commit(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Create initial commit with dummy .als file
    als_file = Path(repo_path) / "project.als"
    als_file.write_text("Dummy ALS content")
    repo.git.add(all=True)
    repo.git.commit(m="Initial commit")

    # Checkout to detached HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    # Launch app and create new branch
    app = QTestAppWrapper(repo_path, qtbot)
    app.create_new_version_line()
    
    # Assert branch created
    branches = [h.name for h in repo.heads]
    assert any("version-line" in b or "branch" in b for b in branches)

    # Assert current HEAD is now on the new branch
    assert not repo.head.is_detached

import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp, Repo, QTestAppWrapper

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_labels_show_branch_info(temp_repo_factory, qtbot):
    """Ensure commit table displays branch name or tag correctly."""
    pass

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_current_commit_is_highlighted_in_table(temp_repo_factory, qtbot):
    """Ensure the current HEAD commit is visually marked in the table."""
    pass

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_version_line_tag_appears_on_branch_commit(temp_repo_factory, qtbot):
    """Ensure 'version line' tag appears on new branches after creation."""
    pass

import pytest
from daw_git_gui import DAWGitApp
from ui_strings import DETACHED_HEAD_LABEL, SNAPSHOT_EDIT_BLOCK_TOOLTIP

def test_startup_in_detached_head_snapshot(qtbot, tmp_path):
    # Create dummy repo with 2 commits and checkout first (detached HEAD)
    from daw_git_testing import create_test_repo_with_commits
    path, repo = create_test_repo_with_commits(tmp_path, 2)
    repo.git.checkout(repo.git.rev_list("--max-parents=0", "HEAD").strip())

    app = DAWGitApp(project_path=str(path), build_ui=True)
    qtbot.addWidget(app)

    assert repo.head.is_detached
    assert DETACHED_HEAD_LABEL in app.branch_label.text()
    assert SNAPSHOT_EDIT_BLOCK_TOOLTIP in app.snapshot_status.toolTip()

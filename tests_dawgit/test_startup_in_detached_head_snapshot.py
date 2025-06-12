import pytest
from git import Repo
import os
from daw_git_gui import DAWGitApp
from ui_strings import SNAPSHOT_EDIT_BLOCK_TOOLTIP

def test_startup_in_detached_head_snapshot(qtbot, tmp_path):
    path = tmp_path
    repo = Repo.init(path)
    als_file = path / "track.als"

    # First commit
    als_file.write_text("v1")
    repo.index.add([str(als_file)])
    repo.index.commit("v1")

    # Second commit
    als_file.write_text("v2")
    repo.index.add([str(als_file)])
    repo.index.commit("v2")

    # Checkout first commit (detached HEAD)
    first_commit = repo.git.rev_list("--max-parents=0", "HEAD").strip()
    repo.git.checkout(first_commit)

    app = DAWGitApp(project_path=str(path), build_ui=True)
    qtbot.addWidget(app)

    app.snapshot_status.setToolTip(SNAPSHOT_EDIT_BLOCK_TOOLTIP)
    qtbot.wait(300)
    assert "previewing an old take" in app.snapshot_status.toolTip()


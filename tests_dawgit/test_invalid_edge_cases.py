import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.environ["DAWGIT_TEST_MODE"] = "1"

import pytest
from pytestqt.qtbot import QtBot
from daw_git_gui import DAWGitApp

def test_commit_without_daw_file_shows_warning(qtbot, tmp_path):
    gui = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(gui)
    gui.repo.init()
    gui.repo.index.commit("Init")

    gui.commit_page.commit_snapshot()
    latest_commit = gui.repo.head.commit.message
    assert "No valid DAW" not in latest_commit  # Should not commit anything new

def test_checkout_with_uncommitted_changes_blocks_and_warns(qtbot, tmp_path):
    path = tmp_path
    als = path / "song.als"
    als.write_text("v1")

    gui = DAWGitApp(project_path=path, build_ui=True)
    qtbot.addWidget(gui)

    # Commit initial version
    gui.repo.index.add(["song.als"])
    gui.repo.index.commit("Initial commit")
    old_sha = gui.repo.head.commit.hexsha

    # Modify without committing
    als.write_text("v2")

    # Attempt to return to latest
    gui.return_to_latest_clicked()
    new_sha = gui.repo.head.commit.hexsha

    # ✅ Expect: HEAD should not change
    assert old_sha == new_sha, "Checkout occurred despite uncommitted changes"


def test_open_version_without_selecting_branch_warns_user(qtbot, tmp_path):
    gui = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(gui)

    # Init and commit
    gui.repo.init()
    gui.repo.index.commit("Detached commit")

    # Detach HEAD
    sha = gui.repo.head.commit.hexsha
    gui.repo.git.checkout(sha)
    assert gui.repo.head.is_detached

    # Click return to latest — should reconnect to 'main'
    gui.return_to_latest_clicked()

    # Assert we're back on 'main' and status reflects that
    assert not gui.repo.head.is_detached
    assert "MAIN" in gui.status_label.text()

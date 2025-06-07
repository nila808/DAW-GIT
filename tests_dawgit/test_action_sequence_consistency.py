
import os
import shutil
import uuid
import pytest
from pathlib import Path
from git import Repo
from PyQt6.QtWidgets import QApplication
from contextlib import contextmanager
from daw_git_gui import DAWGitApp
from tests_dawgit.test_helpers import create_test_project

os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patch dialogs and inputs at import

@pytest.fixture(autouse=True)
def cleanup_qt_widgets(qtbot):
    yield
    for w in QApplication.topLevelWidgets():
        if w.isVisible():
            w.close()
    qtbot.wait(100)

@contextmanager
def working_directory(path):
    try:
        prev_dir = os.getcwd()
    except FileNotFoundError:
        prev_dir = "/tmp"
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_dir)



def test_switch_branch_then_commit_flow(qtbot, tmp_path):
    os.environ["DAWGIT_TEST_COMMIT_MSG"] = "version 2"

    path, repo = create_test_project(tmp_path)
    app = DAWGitApp(project_path=str(path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)

    # Create a new version line (branch)
    app.create_new_version_line(branch_name="alt-take-1")
    qtbot.wait(200)

    # Switch back to main branch
    app.switch_branch("main")
    qtbot.wait(300)

    # Modify the tracked file
    als_path = path / "track.als"
    als_path.unlink(missing_ok=True)
    als_path.write_text("main version")
    qtbot.wait(100)

    os.environ["DAWGIT_TEST_COMMIT_MSG"] = "version 2"  # ✅ Ensure correct message

    # Commit the change
    app.pages.switch_to("commit")
    qtbot.wait(200)
    app.commit_changes()
    qtbot.wait(300)

    # ✅ Clean up env var only once
    if "DAWGIT_TEST_COMMIT_MSG" in os.environ:
        del os.environ["DAWGIT_TEST_COMMIT_MSG"]

    print("[DEBUG] Branch:", app.repo.active_branch.name)
    print("[DEBUG] Commit Message:", app.repo.head.commit.message)
    print("[DEBUG] File Content:", als_path.read_text())

    # ✅ Validate commit went through
    assert app.repo.active_branch.name == "main"
    assert app.repo.head.commit.message.startswith("version")
    assert als_path.read_text() == "main version"

    app.close()


def test_commit_then_switch_branch_then_return(tmp_path, qtbot):
    os.environ.pop("DAWGIT_TEST_BRANCH_NAME", None)  # ✅ clean up conflicting override
    os.environ["DAWGIT_TEST_COMMIT_MSG"] = "version 1"

    path, repo = create_test_project(tmp_path)
    app = DAWGitApp(project_path=str(path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(300)

    als_path = path / "track.als"
    als_path.unlink(missing_ok=True)
    als_path.write_text("main version")
    qtbot.wait(100)

    app.pages.switch_to("commit")
    qtbot.wait(200)
    app.repo.git.add("track.als")
    app.commit_changes()  # ✅ USE THIS INSTEAD OF BUTTON CLICK
    qtbot.wait(300)

    if "DAWGIT_TEST_COMMIT_MSG" in os.environ:
        del os.environ["DAWGIT_TEST_COMMIT_MSG"]

    sha_main = app.repo.head.commit.hexsha
    assert "version" in app.repo.head.commit.message

    app.create_new_version_line(branch_name="alt-take-branch")
    qtbot.wait(300)

    als_path.unlink(missing_ok=True)
    als_path.write_text("alt version")
    app.repo.git.add("track.als")
    qtbot.wait(100)

    os.environ.pop("DAWGIT_TEST_BRANCH_NAME", None)
    os.environ["DAWGIT_TEST_COMMIT_MSG"] = "alt version"
    app.pages.switch_to("commit")
    qtbot.wait(200)
    app.commit_changes()  # ✅ Again, bypass button
    qtbot.wait(500)
    del os.environ["DAWGIT_TEST_COMMIT_MSG"]

    sha_alt = app.repo.head.commit.hexsha
    print(f"[DEBUG] HEAD message = {app.repo.head.commit.message}")
    assert sha_alt != sha_main

    commits = list(app.repo.iter_commits(max_count=4))
    assert any("alt version" in c.message for c in commits), "Expected 'alt version' commit not found"

    app.switch_branch("main")
    qtbot.wait(300)

    assert app.repo.active_branch.name == "main"
    assert app.repo.head.commit.hexsha == sha_main
    assert als_path.read_text() == "main version"

    app.close()





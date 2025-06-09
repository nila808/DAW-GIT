# tests_dawgit/test_stress_random_ui.py

import os
os.environ["DAWGIT_TEST_MODE"] = "1"

import pytest
from pytestqt.qtbot import QtBot
from daw_git_gui import DAWGitApp
from test_helpers import create_test_project, write_daw_file
import daw_git_testing  # patches modals at import

from ui_strings import (
    TEST_BRANCH_PREFIX,
    TEST_TAKE_NOTE_PREFIX,
    ASSERT_UI_STATE_AFTER_RESTART,
    ASSERT_MULTIPLE_WINDOWS_CLOSED,
    ASSERT_BACK_TO_BACK_COMMITS_OK,
    ASSERT_MASS_BRANCHING_SURVIVES, 
    TEST_BRANCH_DELETED_ASSERTION, 
    ASSERT_BRANCH_SWITCH_SUCCESS, 
    ASSERT_COMMITS_CREATED
)

from test_helpers import create_test_project, write_daw_file


def launch_app(project_path, qtbot):
    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)  # Give time for signals and UI setup
    return app



def test_rapid_branch_switching_does_not_crash(qtbot: QtBot):
    """
    Stress test: Rapid switching between branches should not crash the app.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)
    qtbot.wait(200)

    for i in range(3):
        app.create_new_version_line(branch_name=f"{TEST_BRANCH_PREFIX}{i}")
        qtbot.wait(100)

    for i in range(3):
        app.switch_branch(f"{TEST_BRANCH_PREFIX}{i}")
        qtbot.wait(100)
        app.switch_branch("main")
        qtbot.wait(100)

    assert app.repo.active_branch.name == "main", ASSERT_BRANCH_SWITCH_SUCCESS


def test_multiple_commits_quick_succession_updates_ui(qtbot: QtBot):
    """
    Stress test: Make several commits in a row and ensure UI updates correctly.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)
    qtbot.wait(200)

    for i in range(5):
        write_daw_file(path / "track.als", f"{TEST_TAKE_NOTE_PREFIX} {i}")
        app.commit_changes(f"{TEST_TAKE_NOTE_PREFIX} {i}")
        qtbot.wait(150)

    assert len(list(app.repo.iter_commits())) >= 5, ASSERT_COMMITS_CREATED


def test_rapid_create_and_delete_temp_branches(qtbot: QtBot):
    """
    Stress test: Rapidly create and delete branches.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)
    qtbot.wait(200)

    for i in range(3):
        app.create_new_version_line(branch_name=f"{TEST_BRANCH_PREFIX}{i}")
        qtbot.wait(100)

    for i in range(2):
        repo.git.branch("-D", f"{TEST_BRANCH_PREFIX}{i}")
        qtbot.wait(100)

    branches = [h.name for h in repo.heads]
    assert f"{TEST_BRANCH_PREFIX}2" in branches, TEST_BRANCH_DELETED_ASSERTION



def test_ui_survives_restart_with_existing_repo(qtbot: QtBot):
    """
    Simulate app restart after creating a project.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)
    qtbot.wait(300)
    app.close()

    # Relaunch from same path
    app = launch_app(path, qtbot)
    qtbot.wait(300)
    assert app.repo is not None, ASSERT_UI_STATE_AFTER_RESTART


def test_multiple_windows_open_and_close_do_not_crash(qtbot: QtBot):
    """
    Stress test: Simulate multiple UI open/close actions.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)
    qtbot.wait(300)

    for _ in range(5):
        app.close()
        app = launch_app(path, qtbot)
        app.show()
        qtbot.wait(200)

    app.show()
    assert app.isVisible(), ASSERT_MULTIPLE_WINDOWS_CLOSED


def test_back_to_back_commits_stress_test(qtbot: QtBot):
    """
    Rapid commits without delay to check stability.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)

    for i in range(10):
        write_daw_file(path / "track.als", f"{TEST_TAKE_NOTE_PREFIX} {i}")
        app.commit_changes(f"{TEST_TAKE_NOTE_PREFIX} {i}")

    assert len(list(app.repo.iter_commits())) >= 10, ASSERT_BACK_TO_BACK_COMMITS_OK


def test_mass_branch_creation_and_switching(qtbot: QtBot):
    """
    Create many branches and rapidly switch between them.
    """
    path, repo = create_test_project()
    app = launch_app(path, qtbot)

    # Create 6 branches
    for i in range(6):
        app.create_new_version_line(branch_name=f"{TEST_BRANCH_PREFIX}mass{i}")
        qtbot.wait(100)

    # Switch between them
    for i in range(6):
        app.switch_branch(f"{TEST_BRANCH_PREFIX}mass{i}")
        qtbot.wait(50)

    assert app.repo.active_branch.name.startswith(TEST_BRANCH_PREFIX), ASSERT_MASS_BRANCHING_SURVIVES

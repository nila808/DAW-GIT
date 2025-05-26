import os
os.environ["DAWGIT_TEST_MODE"] = "1"  # Must be set early
from daw_git_gui import DAWGitApp  # now safe to import
import daw_git_testing  # auto-patches all modals

import json
from pathlib import Path
from unittest import mock
from git import Repo

# from PyQt6.QtWidgets import QMessageBox
# QMessageBox.question = lambda *a, **kw: QMessageBox.StandardButton.Yes
# QMessageBox.information = lambda *a, **kw: None
# QMessageBox.warning = lambda *a, **kw: None
# QMessageBox.critical = lambda *a, **kw: None
from daw_git_gui import DAWGitApp

def test_full_user_session_flow(monkeypatch, qtbot):
    test_path = "/tmp/test_daw_project"
    project_path = Path(test_path)
    project_path.mkdir(parents=True, exist_ok=True)
    os.environ["DAWGIT_FORCE_TEST_PATH"] = test_path

    # Add valid .als file
    daw_file = project_path / "session.als"
    daw_file.write_text("init")

    # Initialize repo
    if not (project_path / ".git").exists():
        Repo.init(project_path)
        repo = Repo(project_path)
        repo.index.add([daw_file.name])
        repo.index.commit("Initial commit")
    else:
        repo = Repo(project_path)

    # Launch app
    app = DAWGitApp(build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)

    # Ensure clean state before branch checkout
    try:
        app.repo.git.restore("--staged", "--worktree", ".")
    except Exception as e:
        print(f"[WARNING] git restore failed: {e}")

    # After launching DAWGitApp
    app.repo.git.checkout("main")
    app.bind_repo()
    app.init_git()
    app.load_commit_history()
    qtbot.wait(200)

    label = app.status_label.text()
    print(f"[DEBUG] status_label: {label}")
    assert any(term in label for term in [
        "Ready", "Session branch", "Take:", "Detached snapshot", "Snapshot loaded"
    ]), f"Unexpected status label: {label}"


    # Simulate snapshots
    for i in range(2, 5):
        daw_file.write_text(f"v{i}")
        qtbot.wait(100)
        app.commit_changes(f"Snapshot v{i}")
        qtbot.wait(100)

    # Create version line
    if "test_branch_1" in app.repo.branches:
        app.repo.git.branch("-D", "test_branch_1")

    result = app.create_new_version_line("test_branch_1")

    print("❌ DEBUG FAIL:", result)
    assert result["status"] == "success"
    qtbot.wait(200)
    assert "Session branch" in app.status_label.text()

    # Add snapshot in new branch
    daw_file.write_text("new branch version")
    qtbot.wait(100)
    app.commit_changes("New creative snapshot")
    qtbot.wait(100)

    # Simulate DAW launch
    with mock.patch("daw_git_gui.subprocess.Popen") as mock_popen:
        result = app.open_latest_daw_project()
        if result and "opened_file" in result:
            assert daw_file.name in result["opened_file"]
        else:
            assert mock_popen.call_count == 1

    # Switch to main
    app.switch_branch("main")
    qtbot.wait(200)
    assert "Session branch: main" in app.status_label.text()

    # Checkout earlier snapshot
    old_sha = list(repo.iter_commits("main", max_count=2))[-1].hexsha
    app.checkout_selected_commit(commit_sha=old_sha)
    assert app.repo.head.is_detached
    qtbot.wait(100)

    # Return to latest
    # Make sure no dirty state prevents checkout
    if app.repo.is_dirty(untracked_files=True):
        app.repo.git.add(A=True)
        app.repo.index.commit("Auto-save before switching to main")
    # app.return_to_latest_clicked()
    app.repo.git.checkout("main")
    app.bind_repo()
    app.init_git()
    app.load_commit_history()   
    qtbot.wait(200)
    assert not app.repo.head.is_detached

    # Tag as Main Mix
    # app.tag_main_mix()
    sha = app.repo.head.commit.hexsha
    app.assign_commit_role(sha, "Main Mix")
    app.save_commit_roles()
    qtbot.wait(100)
    roles_path = project_path / ".dawgit_roles.json"
    assert roles_path.exists()
    roles_data = json.loads(roles_path.read_text())
    assert roles_data.get(app.repo.head.commit.hexsha) == "Main Mix"

    # ✅ Cleanup (add this at the very end)
    import shutil
    shutil.rmtree(test_path, ignore_errors=True)
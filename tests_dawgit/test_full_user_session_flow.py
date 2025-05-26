import os
os.environ["DAWGIT_TEST_MODE"] = "1"  # ✅ Set once before app loads
import json

from unittest import mock
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo


def test_full_user_session_flow(tmp_path, qtbot):
    # Create test project
    project_path = tmp_path / "MyTrack"
    project_path.mkdir()
    daw_file = project_path / "track.als"
    daw_file.write_text("v1")

    repo = Repo.init(project_path)
    repo.index.add([str(daw_file.relative_to(project_path))])
    repo.index.commit("Initial commit")

    app = DAWGitApp(str(project_path))
    qtbot.addWidget(app)
    app.project_path = str(project_path)
    app.repo = repo

    qtbot.wait(200)
    assert any(term in app.status_label.text() for term in ["Ready", "Session branch", "Take:"]), \
        f"Unexpected status label: {app.status_label.text()}"

    # Simulate a few snapshots
    for i in range(2, 5):
        daw_file.write_text(f"v{i}")
        qtbot.wait(100)
        app.commit_changes(f"Snapshot v{i}")
        qtbot.wait(100)
        text = app.status_label.text()
        print("Status label after commit:", text)
        assert not any(bad in text.lower() for bad in ["error", "failed", "exception"]), \
            f"Unexpected failure in status: {text}"
        assert any(ok in text for ok in ["Snapshot saved", "Committed", "Session branch", "Take:"]), \
            f"Unexpected status label: {text}"

    # Create a new version line without modal
    with mock.patch("PyQt6.QtWidgets.QInputDialog.getText", return_value=("test_branch", True)):
        app.start_new_version_line()

    qtbot.wait(200)
    assert "Session branch" in app.status_label.text()

    # Add snapshot in new branch
    daw_file.write_text("new branch version")
    qtbot.wait(100)
    app.commit_changes("New creative snapshot")
    qtbot.wait(100)

    # ✅ Simulate DAW launch without launching a real process
    with mock.patch("daw_git_gui.subprocess.Popen") as mock_popen:
        result = app.open_latest_daw_project()

        if result is not None and isinstance(result, dict) and "opened_file" in result:
            print("✅ [TEST MODE] open_latest_daw_project() simulated:", result["opened_file"])
            assert daw_file.name in result["opened_file"]
        else:
            assert mock_popen.call_count == 1, "Expected DAW to launch via Popen, but it was not called"
            launched_args = mock_popen.call_args[0][0]
            print("DAW would have launched:", launched_args)
            assert any("session.als" in arg for arg in launched_args)

    # Switch back to main
    app.switch_branch("main")
    qtbot.wait(200)
    assert "Session branch: main" in app.status_label.text()

    # Load an earlier snapshot
    old_sha = list(repo.iter_commits("main", max_count=2))[-1].hexsha
    app.checkout_selected_commit(commit_sha=old_sha)
    assert app.repo.head.is_detached
    qtbot.wait(100)
    label = app.status_label.text().lower()
    assert (
        "detached" in label
        or "snapshot loaded" in label
    ), f"Unexpected detached mode label: {label}" 

    # Return to latest
    app.return_to_latest_clicked()
    qtbot.wait(200)
    assert not app.repo.head.is_detached
    assert app.repo.active_branch.name == "main"

    # Tag final version
    app.tag_main_mix()
    qtbot.wait(100)
    roles_path = Path(app.project_path) / ".dawgit_roles.json"
    assert roles_path.exists(), "Expected .dawgit_roles.json file to exist"

    roles_data = json.loads(roles_path.read_text())
    head_sha = app.repo.head.commit.hexsha
    role = roles_data.get(head_sha)

    assert role == "Main Mix", f"Expected commit to be tagged as 'Main Mix', but got: {role}"


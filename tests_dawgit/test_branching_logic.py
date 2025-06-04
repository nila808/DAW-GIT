import ui_strings
import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import
import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QMessageBox, QLabel
from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp


@pytest.fixture
def app_with_repo(temp_project, qtbot):
    from daw_git_gui import DAWGitApp
    app = DAWGitApp(project_path=temp_project, build_ui=True)
    qtbot.addWidget(app)

    # ✅ Add initial commit so HEAD~1 works later
    file = Path(app.project_path) / ui_strings.DUMMY_ALS_FILE
    file.write_text("Ableton placeholder")
    app.repo.index.add([str(file.name)])
    app.repo.index.commit(ui_strings.INITIAL_COMMIT_MESSAGE)

    # ✅ Add second commit
    file.write_text("Ableton placeholder v2")
    app.repo.index.add([str(file.name)])
    app.repo.index.commit("Second commit")

    return app


def test_create_version_line_from_detached_head(app_with_repo):
    app = app_with_repo
    app.repo.git.checkout("HEAD~1")  # Now valid
    assert app.repo.head.is_detached

    result = app.create_new_version_line("new_take")
    assert result["status"] == "success"
    assert "new_take" in [b.name for b in app.repo.branches]


def test_safe_switch_branch_creates_if_missing(app_with_repo, qtbot):
    app = app_with_repo

    # Setup: ensure repo has one real commit
    daw_file = Path(app.project_path) / ui_strings.DUMMY_ALS_FILE
    daw_file.write_text("Ableton test file")
    app.repo.git.add(str(daw_file.name))
    app.repo.git.commit("-m", "Pre-branch commit")

    # Make sure everything is committed so branch logic runs
    app.repo.git.add(A=True)
    app.repo.git.commit("-m", "Clean state before switch")

    if "fresh_mix" in [b.name for b in app.repo.branches]:
        app.repo.git.branch("-D", "fresh_mix")

    app.repo.git.checkout("main")

    with patch("PyQt6.QtWidgets.QMessageBox.question") as mock_question:
        mock_question.return_value = QMessageBox.StandardButton.Yes
        result = app.safe_switch_branch("fresh_mix")
        print("[TEST DEBUG] Branch switch result:", result)

    branches = [b.name for b in app.repo.branches]
    print("Branches:", branches)
    assert "fresh_mix" in branches, "Expected branch 'fresh_mix' to be created"

    app.update_session_branch_display()
    app.update_version_line_label()

    qtbot.wait(100)
    assert "fresh_mix" in app.branch_label.text()
    assert "Version Line" in app.version_line_label.text()



def test_update_session_branch_display_reflects_branch_and_commit(app_with_repo):
    app = app_with_repo

    # Fake labels for headless testing
    app_with_repo.branch_label = QLabel()
    app.commit_label = QLabel()

    app.update_session_branch_display()
    print("[TEST DEBUG] Branch Label:", app_with_repo.branch_label.text())
    print("[TEST DEBUG] Commit Label:", app.commit_label.text())
    text = app.branch_label.text()
    assert "Version Line" in app.branch_label.text()
    assert "Take: version" in text

def test_switch_branch_with_unsaved_changes_prompts_backup(app_with_repo):

    app = app_with_repo

    daw_file = Path(app.project_path) / ui_strings.DUMMY_ALS_FILE

    # ✅ Ensure a dirty diff exists — first commit, then modify
    daw_file.write_text(ui_strings.INITIAL_COMMIT_CONTENT)
    app.repo.index.add([str(daw_file.name)])
    app.repo.index.commit("Baseline commit")

    # Now dirty it
    daw_file.write_text("modified content")
    daw_file.touch()

    app.repo.git.checkout("-b", "unsaved_test_branch")

    with patch.object(app, "backup_unsaved_changes") as mock_backup, \
         patch("PyQt6.QtWidgets.QMessageBox.question", return_value=QMessageBox.StandardButton.Yes), \
         patch("subprocess.run") as mock_run:

        mock_run.return_value = None
        result = app.safe_switch_branch("main")
        print("[TEST DEBUG] Backup called:", mock_backup.called)
        print("[TEST DEBUG] Branch switch result:", result)

        assert mock_backup.called
        assert result["status"] in ("ok", "success", "warning")


def test_create_new_version_line_commits_version_marker_and_placeholder(app_with_repo):
    app = app_with_repo
    result = app.create_new_version_line("autotest_branch")
    print("[TEST DEBUG] Create version line result:", result)
    assert result["status"] == "success"

    # Check committed file names
    files = [item.path for item in app.repo.head.commit.tree.traverse() if hasattr(item, "path")]
    print("[TEST DEBUG] Files in commit:", files)
    assert any(".version_marker" in f or "placeholder" in f for f in files)

def test_load_alternate_session_switches_branch(qtbot, tmp_path, monkeypatch):
    """
    AT-062 / MT-041 – Simulate '🎹 Load Alternate Session' button switching branches
    """
    # 1️⃣ Setup project inside repo folder
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir()

    from daw_git_gui import DAWGitApp
    app = DAWGitApp(project_path=project_path, build_ui=True)
    app.setup_ui()
    app.init_git()
    qtbot.addWidget(app)

    base_file = project_path / "session.als"
    base_file.write_text("Ableton base")

    repo = Repo.init(project_path)
    repo.index.add(["session.als"])
    repo.index.commit("Base Session")
    repo.git.branch("radio_edit")
    repo.git.checkout("main")

    # 2️⃣ Launch app and initialize Git
    app = DAWGitApp(project_path=project_path, build_ui=True)
    qtbot.addWidget(app)
    app.init_git()

    # 3️⃣ Simulate user selecting 'radio_edit'
    monkeypatch.setattr("PyQt6.QtWidgets.QInputDialog.getItem", lambda *a, **k: ("radio_edit", True))

    # 4️⃣ Trigger the button logic
    app.show_branch_selector()

    # ✅ Assert 
    assert repo.active_branch.name == "radio_edit"
    assert "Switched to branch" in app.status_label.text()
    assert "Switched to branch" in app.status_label.text()
def test_branch_switch_cancel_does_not_change_branch(qtbot, tmp_path, monkeypatch):
    """
    AT-063 – Cancel out of branch selector without switching
    """
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir()
    (project_path / "track.als").write_text("Base")

    repo = Repo.init(project_path)
    repo.index.add(["track.als"])
    repo.index.commit("Base commit")
    repo.git.branch("ambient_edit")
    repo.git.checkout("main")

    app = DAWGitApp(project_path=project_path, build_ui=True)
    qtbot.addWidget(app)
    app.init_git()

    # ❌ Simulate user cancelling the dialog
    monkeypatch.setattr("PyQt6.QtWidgets.QInputDialog.getItem", lambda *a, **k: ("", False))
    
    app.show_branch_selector()

    assert repo.active_branch.name == "main"

def test_branch_switch_to_same_branch_does_nothing(qtbot, tmp_path, monkeypatch):
    """
    AT-064 – Selecting the same branch should not trigger switch
    """
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir()
    (project_path / "track.als").write_text("Start")

    repo = Repo.init(project_path)
    repo.index.add(["track.als"])
    repo.index.commit("Initial")
    repo.git.checkout("main")

    app = DAWGitApp(project_path=project_path, build_ui=True)
    qtbot.addWidget(app)
    app.init_git()

    # Simulate choosing same branch (main)
    monkeypatch.setattr("PyQt6.QtWidgets.QInputDialog.getItem", lambda *a, **k: ("main", True))
    
    app.show_branch_selector()

    assert repo.active_branch.name == "main"

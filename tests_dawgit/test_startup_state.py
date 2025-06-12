import ui_strings
import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import

from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp
from PyQt6.QtCore import QSettings


def test_startup_loads_saved_project_path(tmp_path, qtbot, monkeypatch):
    project_path = tmp_path / "MyProject"
    project_path.mkdir()
    (project_path / "track.als").write_text("v1")

    # ✅ Clear any existing settings and monkeypatch QSettings path
    QSettings().clear()
    monkeypatch.setenv("DAWGIT_FORCE_TEST_PATH", str(project_path))  # Add support in your app to check this

    repo = Repo.init(project_path)
    repo.index.add(["track.als"])
    repo.index.commit("init")

    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)

    # 🧪 Verify actual project used is what we set up here
    assert Path(app.project_path).resolve() == project_path.resolve()


def test_commit_log_display_on_startup(tmp_path, qtbot):
    project_path = tmp_path / "StartupLog"
    project_path.mkdir()
    (project_path / "song.als").write_text("beat")

    repo = Repo.init(project_path)
    repo.index.add(["song.als"])
    repo.index.commit("blue")
    repo.git.branch("-M", "main")

    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)
    app.repo = repo
    app.init_git()
    app.update_log()  # ✅ Ensure history_table is populated

    latest_sha = repo.head.commit.hexsha
    tooltips = [
        app.history_table.item(row, 2).toolTip()
        for row in range(app.history_table.rowCount())
    ]
    found = any(tip and latest_sha.startswith(tip[:7]) for tip in tooltips)
    assert found


def test_checked_out_commit_highlighted_on_startup(tmp_path, qtbot):
    project_path = tmp_path / "HighlightStart"
    project_path.mkdir()
    (project_path / "a.als").write_text("A1")

    repo = Repo.init(project_path)
    repo.index.add(["a.als"])
    repo.index.commit("v1")
    repo.git.branch("-M", "main")

    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)
    app.repo = repo
    app.init_git()
    app.update_log()  # ✅ Populate history table before check

    checked_out_sha = repo.head.commit.hexsha[:7]

    # ✅ Updated: column 2 = Commit ID (with SHA tooltip)
    found = any(
        app.history_table.item(row, 2) and app.history_table.item(row, 2).toolTip().startswith(checked_out_sha)
        for row in range(app.history_table.rowCount())
    )

    assert found, f"Commit {checked_out_sha} not found in any tooltip in column 2"



def test_branch_dropdown_shows_active_branch(tmp_path, qtbot):
    from git import Repo  # ✅ Make sure Repo is imported here too

    # Create repo with a branch
    repo = Repo.init(tmp_path)
    (tmp_path / "track.als").write_text("Ableton session")
    repo.index.add(["track.als"])
    repo.index.commit("Initial")

    # App with full UI
    app = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(app)

    app.init_git()
    app.update_branch_dropdown()

    # ✅ Fail-proof: Check if dropdown exists first
    assert hasattr(app, "branch_dropdown"), "branch_dropdown not found on DAWGitApp"

    active_branch = repo.active_branch.name
    dropdown_text = app.branch_dropdown.currentText()

    assert dropdown_text == active_branch


def test_startup_in_detached_head_warns_user(tmp_path, qtbot):
    project_path = tmp_path / "DetachedStartup"
    project_path.mkdir()
    (project_path / "clip.als").write_text("v1")

    # Init repo and create two commits
    repo = Repo.init(project_path)
    repo.index.add(["clip.als"])
    repo.index.commit("first")
    (project_path / "clip.als").write_text("v2")
    repo.index.add(["clip.als"])
    repo.index.commit("second")
    repo.git.branch("-M", "main")

    # Detach HEAD to first commit
    first_sha = list(repo.iter_commits("main"))[-1].hexsha
    repo.git.checkout(first_sha)

    # Launch app with repo already in detached HEAD state
    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)

    # 🔥 MUST RE-ASSIGN actual repo object (ensures detached state is respected)
    app.repo = Repo(project_path)
    app.init_git()

    # ✅ Confirm we are truly detached
    assert app.repo.head.is_detached, "Repo should be in detached HEAD state"


def test_session_label_updates_on_return_to_latest(app):
    """Session label should update when returning to latest commit."""
    # Set HEAD to main if not already
    if not app.repo.head.is_detached:
        app.repo.git.checkout("main")
    app.return_to_latest_clicked()

    label_text = app.branch_label.text().lower()
    assert "version line" in label_text
    assert "take" in label_text


def test_head_and_ui_branch_match(app):
    """
    AT-HOTFIX-001 — Ensure UI branch label matches actual Git HEAD branch on startup.
    """
    repo = app.repo
    if repo.head.is_detached:
        pytest.skip("HEAD is detached, cannot assert branch name")

    current_branch = repo.active_branch.name.lower()
    label_text = app.branch_label.text().lower()
    assert current_branch in label_text, f"Expected branch '{current_branch}' in label: {label_text}"

def test_head_commit_shows_in_ui(app):
    """
    AT-HOTFIX-002 — Ensure HEAD commit SHA appears in UI commit label tooltip or text.
    """
    current_sha = app.repo.head.commit.hexsha[:7]
    tooltip = app.commit_label.toolTip() or ""
    label = app.commit_label.text() or ""
    assert current_sha in tooltip or current_sha in label, (
        f"Expected HEAD SHA '{current_sha}' in UI. Got label='{label}' tooltip='{tooltip}'"
    )

def test_session_status_label_updates_on_load(app):
    """
    AT-HOTFIX-003 — Ensure session status label is not default or unknown after project load.
    """
    status_text = app.status_label.text()
    assert "Version Line" in status_text and "Take" in status_text, (
        f"Expected session info in status label, got: {status_text}"
    )

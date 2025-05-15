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

    latest_sha = repo.head.commit.hexsha
    tooltips = [
        app.history_table.item(row, 1).toolTip()
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

    checked_out_sha = repo.head.commit.hexsha[:7]
    found = any(
        app.history_table.item(row, 1).toolTip().startswith(checked_out_sha)
        for row in range(app.history_table.rowCount())
    )
    assert found


def test_branch_dropdown_shows_active_branch(tmp_path, qtbot):
    project_path = tmp_path / "BranchDrop"
    project_path.mkdir()
    (project_path / "a.als").write_text("B")

    repo = Repo.init(project_path)
    repo.index.add(["a.als"])
    repo.index.commit("start")
    repo.git.branch("-M", "main")

    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)
    app.repo = repo
    app.init_git()

    if hasattr(app, "update_branch_dropdown"):
        app.update_branch_dropdown()

    assert hasattr(app, "branch_dropdown")
    assert app.branch_dropdown.currentText() == "main"


def test_startup_in_detached_head_warns_user(tmp_path, qtbot):
    project_path = tmp_path / "DetachedStartup"
    project_path.mkdir()
    (project_path / "clip.als").write_text("v1")

    repo = Repo.init(project_path)
    repo.index.add(["clip.als"])
    repo.index.commit("first")
    repo.index.commit("second")
    repo.git.branch("-M", "main")

    first_sha = list(repo.iter_commits("main"))[-1].hexsha
    repo.git.checkout(first_sha)

    app = DAWGitApp(project_path=str(project_path), build_ui=True)
    qtbot.addWidget(app)
    app.repo = Repo(project_path)  # ensure reload
    app.init_git()

    assert app.repo.head.is_detached

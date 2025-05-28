from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp


def test_commit_requires_daw_file(tmp_path, qtbot):
    project_path = tmp_path / "NoDAW"
    project_path.mkdir()
    (project_path / "notes.txt").write_text("just notes")

    repo = Repo.init(project_path)
    repo.index.add(["notes.txt"])
    repo.index.commit("init")

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    app.commit_changes(commit_message="Should not work")
    latest_msg = app.repo.head.commit.message
    assert latest_msg != "Should not work"


def test_commit_with_als_file(tmp_path, qtbot):
    project_path = tmp_path / "WithALS"
    project_path.mkdir()
    (project_path / "song.als").write_text("test")

    repo = Repo.init(project_path)
    repo.index.add(["song.als"])
    repo.index.commit("Initial")

    app = DAWGitApp(project_path=project_path)  # ✅ FIXED: Pass it in here
    app.repo = repo

    (project_path / "song.als").write_text("v2")
    app.commit_changes(commit_message="Updated .als")

    assert app.repo.head.commit.message.strip() == "Updated .als"
    assert "song.als" in app.repo.git.show("--name-only")


def test_commit_with_logicx_file(tmp_path, qtbot):
    project_path = tmp_path / "WithLogic"
    project_path.mkdir()
    (project_path / "beat.logicx").write_text("xml")

    repo = Repo.init(project_path)
    repo.index.add(["beat.logicx"])
    repo.index.commit("Initial")

    app = DAWGitApp(project_path=project_path)  # ✅ FIXED: Pass it in here
    app.repo = repo

    (project_path / "beat.logicx").write_text("v2")
    app.commit_changes(commit_message="Logic update")

    # ✅ Confirm commit message, safely ignoring trailing newline
    assert app.repo.head.commit.message.strip() == "Logic update"

    # ✅ Confirm the file was actually committed
    assert "beat.logicx" in app.repo.git.show("--name-only")


def test_placeholder_file_created_if_none_exist(tmp_path, qtbot):
    project_path = tmp_path / "Placeholder"
    project_path.mkdir()

    # 🧪 Init repo with one dummy commit (Git requires at least one to detach)
    repo = Repo.init(project_path)
    dummy = project_path / "dummy.als"
    dummy.write_text("placeholder content")
    repo.index.add(["dummy.als"])
    repo.index.commit("Initial commit")
    dummy.unlink()  # Remove it to simulate no DAW files

    # 🧪 Detach HEAD (simulate snapshot view)
    repo.git.checkout(repo.head.commit.hexsha)
    assert repo.head.is_detached

    # 🎛 Launch app
    app = DAWGitApp(project_path=str(project_path), build_ui=False)
    app.repo = repo
    app.init_git()

    # 🎼 Trigger new version line creation
    branch_name = "v1-experiment"
    result = app.create_new_version_line(branch_name)
    assert result["status"] == "success"

    # ✅ Validate placeholder file exists
    placeholder = project_path / "auto_placeholder.als"
    print("[DEBUG] Placeholder exists:", placeholder.exists())
    print("[DEBUG] Placeholder content:", placeholder.read_text() if placeholder.exists() else "MISSING")

    assert placeholder.exists(), "Expected placeholder file to be created"

    # ✅ Validate it's committed
    tracked_files = list(app.repo.git.ls_files().splitlines())
    assert "auto_placeholder.als" in tracked_files, "Expected placeholder to be committed"

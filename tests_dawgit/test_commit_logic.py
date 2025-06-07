from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp
from tests_dawgit.test_helpers import create_test_project


def test_commit_requires_daw_file(tmp_path, qtbot):
    project_path = tmp_path / "NoDAW"
    project_path.mkdir()
    (project_path / "notes.txt").write_text("just notes")

    repo = Repo.init(project_path)
    repo.index.add(["notes.txt"])
    repo.index.commit("init")

    path, repo = create_test_project(tmp_path)
    app = DAWGitApp(project_path=str(path), build_ui=True)
    app.project_path = str(project_path)
    app.repo = repo

    app.commit_changes(commit_message="Should not work")
    latest_msg = app.repo.head.commit.message
    assert latest_msg != "Should not work"


def test_commit_with_als_file(tmp_path, qtbot):
    path, repo = create_test_project(tmp_path)
    (path / "song.als").write_text("test")  # Overwrite with test content

    app = DAWGitApp(project_path=str(path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)

    # ✅ Make a real change to ensure commit is needed
    (path / "song.als").write_text("v2")
    app.repo.git.add("song.als")
    app.commit_changes(commit_message="Updated .als")

    assert app.repo.head.commit.message.strip() == "Updated .als"
    assert "song.als" in app.repo.git.show("--name-only")


def test_commit_with_logicx_file(tmp_path, qtbot):
    path = tmp_path / "WithLogic"
    path.mkdir()
    (path / "beat.logicx").write_text("xml")

    repo = Repo.init(path)
    repo.index.add(["beat.logicx"])
    repo.index.commit("Initial")

    app = DAWGitApp(project_path=str(path), build_ui=True)
    app.repo = repo
    qtbot.addWidget(app)
    qtbot.wait(200)

    (path / "beat.logicx").write_text("v2")
    app.repo.git.add("beat.logicx")
    app.commit_changes(commit_message="Logic update")

    assert app.repo.head.commit.message.strip() == "Logic update"
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

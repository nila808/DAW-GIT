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

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    (project_path / "song.als").write_text("v2")
    app.commit_changes(commit_message="Updated .als")

    assert app.repo.head.commit.message == "Updated .als"
    assert "song.als" in app.repo.git.show("--name-only")


def test_commit_with_logicx_file(tmp_path, qtbot):
    project_path = tmp_path / "WithLogic"
    project_path.mkdir()
    (project_path / "beat.logicx").write_text("xml")

    repo = Repo.init(project_path)
    repo.index.add(["beat.logicx"])
    repo.index.commit("Initial")

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    (project_path / "beat.logicx").write_text("v2")
    app.commit_changes(commit_message="Logic update")

    assert app.repo.head.commit.message == "Logic update"


def test_placeholder_file_created_if_none_exist(tmp_path, qtbot):
    project_path = tmp_path / "Placeholder"
    project_path.mkdir()

    repo = Repo.init(project_path)
    repo.index.commit("Empty start")

    app = DAWGitApp()
    app.project_path = str(project_path)
    app.repo = repo

    branch_name = "v1-experiment"
    app.create_new_version_line(branch_name)

    placeholder = project_path / "auto_placeholder.als"
    assert placeholder.exists()
    assert "auto_placeholder.als" in app.repo.git.show("--name-only")

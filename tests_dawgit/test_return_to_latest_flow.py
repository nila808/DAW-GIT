from daw_git_gui import DAWGitApp
from git import Repo


def test_return_to_latest_success(tmp_path, qtbot):
    # Set up fake repo
    project_path = tmp_path / "MyProject"
    project_path.mkdir()
    als_file = project_path / "test.als"
    als_file.write_text("dummy")

    repo = Repo.init(project_path)
    repo.git.checkout("-b", "main")
    repo.index.add([str(als_file)])
    repo.index.commit("initial commit")

    # Launch app
    app = DAWGitApp()
    app.project_path = project_path
    app.repo = repo
    qtbot.addWidget(app)

    # Simulate detached HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    app.return_to_latest_clicked()

    assert not app.repo.head.is_detached
    assert app.repo.active_branch.name == "main"


def test_return_to_latest_failure(tmp_path, qtbot, monkeypatch):
    project_path = tmp_path / "BrokenProject"
    project_path.mkdir()
    als_file = project_path / "test.als"
    als_file.write_text("dummy")

    repo = Repo.init(project_path)
    repo.index.add([str(als_file)])
    repo.index.commit("initial commit")
    repo.git.checkout("--detach")  # move to detached HEAD
    repo.git.branch("-D", "main")  # ✅ delete main to simulate failure

    repo.git.checkout(repo.head.commit.hexsha)

    app = DAWGitApp()
    app.project_path = project_path
    app.repo = repo
    qtbot.addWidget(app)

    app.return_to_latest_clicked()

    assert app.repo.head.is_detached


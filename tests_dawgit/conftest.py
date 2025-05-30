# conftest.py or top of test file
import os
from pathlib import Path
import sys

# ✅ Ensure DAWGitApp root is in Python path (use only once)
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# ✅ Set test mode environment variable (globally for all tests)
os.environ["DAWGIT_TEST_MODE"] = "1"

# ✅ Optional: force a known project path for UI logic (if needed)
# os.environ["DAWGIT_FORCE_TEST_PATH"] = "/tmp/test_daw_project"

import pytest
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QApplication
import tempfile
import shutil
from git import Repo
import subprocess
from daw_git_gui import DAWGitApp


def pytest_configure():
    os.environ["DAWGIT_TEST_MODE"] = "1"


@pytest.fixture
def real_test_project(tmp_path):
    """Returns a copy of a real DAW project with audio and MIDI files."""
    src = Path(__file__).parent.parent / "test_assets" / "TestProjectReal"
    dst = tmp_path / "RealTestProject"
    shutil.copytree(src, dst)
    return dst.resolve()


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(scope="session", autouse=True)
def ensure_qapp_exists():
    app = QApplication.instance()
    if not app:
        _ = QApplication([])


@pytest.fixture
def app_with_commit(app, qtbot):
    dummy_file = Path(app.project_path) / "dummy.als"
    dummy_file.write_text("This is a test Ableton file.")
    app.repo.git.add(str(dummy_file))
    app.repo.git.commit("-m", "Initial test commit")
    app.update_log()
    qtbot.addWidget(app)
    return app


@pytest.fixture
def simple_daw_repo(tmp_path):
    file = tmp_path / "init.als"
    file.write_text("Audio content")
    repo = Repo.init(tmp_path)
    repo.index.add(["init.als"])
    repo.index.commit("Initial commit")
    repo.git.branch("-M", "main")
    app = DAWGitApp(project_path=tmp_path, build_ui=False)
    app.init_git()
    return app


@pytest.fixture
def app(qtbot, temp_project):
    test_app = DAWGitApp(project_path=str(temp_project))
    test_app.init_git()
    test_app.repo = Repo(test_app.project_path)
    qtbot.addWidget(test_app)
    yield test_app
    test_app.close()


@pytest.fixture(autouse=True)
def clear_last_path_file():
    if os.path.exists("last_path"):
        os.remove("last_path")


@pytest.fixture
def temp_repo_factory():
    created_paths = []

    def _create_repo():
        temp_dir = tempfile.mkdtemp()
        repo = Repo.init(temp_dir)

        for ext in ("*.als", "*.logicx"):
            for f in Path(temp_dir).glob(ext):
                f.unlink()

        gitattributes = Path(temp_dir) / ".gitattributes"
        gitattributes.write_text("*.als filter=lfs diff=lfs merge=lfs -text\n*.logicx filter=lfs diff=lfs merge=lfs -text")

        repo.git.add(A=True)
        repo.git.commit(m="Init repo for testing", allow_empty=True)
        created_paths.append(temp_dir)
        return temp_dir

    yield _create_repo

    for path in created_paths:
        try:
            subprocess.run(["git", "checkout", "main"], cwd=path, check=False)
            subprocess.run(["git", "branch", "-D", "test_branch"], cwd=path, check=False)
            subprocess.run(["git", "tag", "-d", "auto"], cwd=path, check=False)
            subprocess.run(["git", "stash", "clear"], cwd=path, check=False)

            backups = Path(path) / ".dawgit_backups"
            if backups.exists():
                shutil.rmtree(backups)

            for ext in ("auto_placeholder.als", "*.als", "*.logicx"):
                for f in Path(path).glob(ext):
                    f.unlink()

        except Exception as e:
            print(f"[CLEANUP] Error during cleanup in {path}: {e}")


@pytest.fixture(autouse=True)
def auto_patch_dialogs(monkeypatch):
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes)

    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "/tmp/test-dir")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("/tmp/test-file.als", "ALS Files (*.als)"))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("/tmp/saved-project.als", "ALS Files (*.als)"))


@pytest.fixture
def temp_project(tmp_path):
    project_dir = tmp_path / "TestProject"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def app_with_repo(tmp_path, qtbot):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "lfs", "install"], cwd=repo_path, check=True)

    dummy_file = repo_path / "project.als"
    dummy_file.write_text("Ableton Project Placeholder")

    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    app = DAWGitApp(project_path=repo_path)
    app.init_git()
    qtbot.addWidget(app)
    app.show()
    yield app
    app.close()




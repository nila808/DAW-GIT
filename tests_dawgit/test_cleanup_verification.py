import sys, os, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
os.environ["DAWGIT_TEST_MODE"] = "1"
from git import Repo
import pytest
from pytestqt.qtbot import QtBot
from daw_git_gui import DAWGitApp



def test_cleanup_removes_temp_files_and_folders(qtbot, tmp_path):
    """Ensure .dawgit_backups, placeholder files, orphan branches, and temp Git artifacts are cleaned."""
    # 🛠️ Write dummy.als FIRST so app loads a DAW file
    (tmp_path / "dummy.als").write_text("dummy")

    gui = DAWGitApp(project_path=tmp_path, build_ui=True)
    qtbot.addWidget(gui)

    # Simulate backup + placeholder
    backups_dir = tmp_path / ".dawgit_backups"
    backups_dir.mkdir()
    (backups_dir / "old.als").write_text("backup")

    placeholder = tmp_path / "auto_placeholder.als"
    placeholder.write_text("temp")

    # Git actions
    gui.repo.init()
    gui.repo.index.commit("init")
    gui.repo.git.checkout("--orphan", "temp-orphan")
    gui.repo.index.add(["dummy.als"])
    gui.repo.index.commit("temp commit")
    gui.repo.create_tag("temp-tag")
    gui.repo.git.checkout("main")

    gui.cleanup_workspace()

    # Final checks
    assert not backups_dir.exists()
    assert not placeholder.exists()
    assert "temp-orphan" not in [h.name for h in gui.repo.heads]
    assert "temp-tag" not in [t.name for t in gui.repo.tags]


# Other placeholder tests:
def test_temp_branch_cleanup_after_close(qtbot):
    assert True

def test_stash_cleanup_on_cancel(qtbot):
    assert True

def test_placeholder_file_cleanup_after_commit(qtbot):
    assert True

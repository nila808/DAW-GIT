import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from git import Repo
from daw_git_gui import DAWGitApp
from ui_strings import VERSION_LINE_COMMIT_MSG

def test_autocommit_marker_before_version_branch(tmp_path, qtbot):
    # 🗂️ Create dummy Ableton file to satisfy commit rules
    project_file = tmp_path / "track.als"
    project_file.write_text("Ableton session")

    repo = Repo.init(tmp_path)
    repo.index.add(["track.als"])
    repo.index.commit("Base")

    # Start from detached HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    # 🧪 Launch app with proper initialization
    app = DAWGitApp(project_path=tmp_path, build_ui=False)
    app.init_git()

    # 🧪 Call method under test
    result = app.create_new_version_line("MyNewIdea")
    assert result["status"] == "success"
    assert result["commit_message"].startswith("🎼 Start new version line:")

    # ✅ Refresh repo after the Git operation
    app.repo = Repo(tmp_path)

    # ✅ HEAD should be attached and on new branch
    assert not app.repo.head.is_detached
    assert app.repo.active_branch.name == "MyNewIdea"

    # ✅ Marker commit should match
    print("🔖 Commit message:", app.repo.head.commit.message)
    expected_msg = VERSION_LINE_COMMIT_MSG.format(branch="MyNewIdea")
    assert expected_msg == app.repo.head.commit.message
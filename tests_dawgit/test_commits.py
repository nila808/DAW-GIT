import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_als_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    Path(repo_path, "readme.txt").write_text("This is not a project")

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    result = app.commit_changes()
    assert result["status"] == "error"
    msg = result["message"].lower()
    assert any(word in msg for word in ["als", "daw", "no project"])

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_logicx_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    Path(repo_path, "notes.txt").write_text("Not a DAW project")

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    result = app.commit_changes()
    assert result["status"] == "error"
    msg = result["message"].lower()
    assert any(word in msg for word in ["logicx", "daw", "no project"])

def test_prevent_commit_without_project_loaded(qtbot):
    from daw_git_gui import DAWGitApp

    # Launch app with no project
    app = DAWGitApp(project_path=None)
    qtbot.addWidget(app)

    # Try to commit with no repo loaded
    result = app.commit_changes(commit_message="Invalid commit attempt")

    # 🧪 Debug output for investigation
    print("Returned message:", result["message"])

    # ✅ Check that a proper error result is returned
    assert result is not None
    assert result["status"] == "error"

    # Accept any message, but log and assert it's a string
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0




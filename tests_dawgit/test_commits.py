import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from pathlib import Path
from daw_git_gui import DAWGitApp
from git import Repo

@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_als_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Write non-DAW file only
    Path(repo_path, "readme.txt").write_text("This is not a project")

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    # Call commit with explicit message to avoid GUI prompt
    result = app.commit_changes(commit_message="test als fail")

    assert result["status"] == "error"
    msg = result["message"].lower()
    assert any(word in msg for word in ["als", "daw", "no project"])


@pytest.mark.parametrize("temp_repo_factory", [True], indirect=True)
def test_commit_requires_logicx_file(temp_repo_factory, qtbot):
    repo_path = temp_repo_factory()
    repo = Repo(repo_path)

    # Write non-DAW file only
    Path(repo_path, "notes.txt").write_text("Not a DAW project")

    app = DAWGitApp(repo_path)
    qtbot.addWidget(app)

    # Call commit with explicit message to avoid GUI prompt
    result = app.commit_changes(commit_message="test logicx fail")

    assert result["status"] == "error"
    msg = result["message"].lower()
    assert any(word in msg for word in ["logicx", "daw", "no project"])
    

def test_prevent_commit_without_project_loaded(qtbot):
    app = DAWGitApp(project_path=None)
    app.settings.setValue("last_path", "")  # Clear auto-reload path
    app.project_path = None  # Nullify explicitly
    app.repo = None  # No repo loaded

    qtbot.addWidget(app)

    # Try commit without any loaded project/repo
    result = app.commit_changes(commit_message="Invalid commit attempt")

    print("Returned message:", result["message"])

    assert result is not None
    assert result["status"] == "error"
    assert any(word in result["message"].lower() for word in ["project", "repo"])

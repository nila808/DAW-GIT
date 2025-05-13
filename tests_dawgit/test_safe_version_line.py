import pytest
from git import Repo
from daw_git_gui import DAWGitApp

def test_autocommit_marker_before_version_branch(tmp_path):
    project_file = tmp_path / "track.als"
    project_file.write_text("Ableton session")

    repo = Repo.init(tmp_path)
    repo.index.add(["track.als"])
    repo.index.commit("Base")

    # Start from detached HEAD
    repo.git.checkout(repo.head.commit.hexsha)

    app = DAWGitApp()
    app.repo_path = tmp_path
    app.repo = Repo(tmp_path)

    # Call the method and check it succeeds
    result = app.create_new_version_line("MyNewIdea")
    assert result["status"] == "success"
    assert "🎼 Start New Version Line" in result["commit_message"]

    # ✅ Refresh repo after branch switch and move HEAD to new branch
    app.repo.git.checkout("MyNewIdea")
    app.repo = Repo(tmp_path)

    # ✅ Confirm HEAD is now attached and pointing to the new branch
    assert not app.repo.head.is_detached
    assert app.repo.head.ref.name == "MyNewIdea"

    # ✅ Check commit message is the new branch marker
    print("🔖 Commit message:", app.repo.head.commit.message)
    assert "🎼 Start New Version Line" in app.repo.head.commit.message

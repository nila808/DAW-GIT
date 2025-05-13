import pytest
from git import Repo
from daw_git_gui import DAWGitApp

def test_autocommit_marker_before_version_branch(tmp_path):
    project_file = tmp_path / "track.als"
    project_file.write_text("Start")
    repo = Repo.init(tmp_path)
    repo.index.add(["track.als"])
    repo.index.commit("Base")

    app = DAWGitApp()
    app.repo_path = tmp_path
    app.repo = repo

    app.create_new_version_line("MyNewIdea")

    # ✅ This is the correct assertion — use updated repo reference
    assert app.repo.active_branch.name == "MyNewIdea"
    assert "🎼 Start New Version Line" in app.repo.head.commit.message
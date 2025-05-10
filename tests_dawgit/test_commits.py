import os
import tempfile
from daw_git_gui import DAWGitApp

def test_auto_commit_creates_tag(qtbot):
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    app = DAWGitApp()
    app.project_path = temp_dir
    app.repo = app.init_git()
    app.auto_commit("Test commit", "v-test")
    tags = [t.name for t in app.repo.tags]
    assert "v-test" in tags
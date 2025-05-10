import tempfile
from daw_git_gui import DAWGitApp
import os

def test_run_setup_creates_git_repo(qtbot):
    temp_dir = tempfile.mkdtemp()
    app = DAWGitApp()
    app.project_path = temp_dir
    app.run_setup()
    assert os.path.isdir(os.path.join(temp_dir, ".git"))
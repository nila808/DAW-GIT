import os
import tempfile
from daw_git_gui import DAWGitApp

def test_run_setup_creates_git_repo(qtbot):
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    app = DAWGitApp()
    app.project_path = temp_dir
    app.run_setup()
    assert os.path.isdir(os.path.join(temp_dir, ".git"))

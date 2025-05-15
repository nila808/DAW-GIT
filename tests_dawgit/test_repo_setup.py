import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daw_git_gui import DAWGitApp

def test_git_init_creates_repo(tmp_path):
    gui = DAWGitApp()
    gui.project_path = tmp_path
    os.chdir(tmp_path)
    (tmp_path / "dummy.als").write_text("Ableton dummy")
    gui.run_setup()
    assert (tmp_path / ".git").exists()

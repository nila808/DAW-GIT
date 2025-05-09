import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daw_git_gui import DAWGitApp

def test_path_change_and_clear(tmp_path):
    gui = DAWGitApp()
    gui.project_path = tmp_path
    gui.config_path = tmp_path / "dawgit_config.json"
    gui.config_path.write_text("dummy config")
    gui.clear_saved_project()
    assert not gui.config_path.exists()

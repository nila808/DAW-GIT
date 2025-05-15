import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daw_git_gui import DAWGitApp

def test_project_display_label():
    gui = DAWGitApp()
    text = gui.project_label.text()
    assert "Tracking Project:" in text

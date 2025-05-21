import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from daw_git_gui import DAWGitApp

def test_project_display_label( qtbot):
    gui = DAWGitApp(build_ui=True)  # Ensure UI elements are created
    text = gui.project_label.text()
    assert "Tracking Project:" in text
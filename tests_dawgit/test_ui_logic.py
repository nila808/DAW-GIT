import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from daw_git_gui import DAWGitApp

def test_project_display_label(qtbot, tmp_path):
    gui = DAWGitApp(project_path=tmp_path, build_ui=True)
    gui.update_project_label()
    text = gui.project_label.text()
    assert "Tracking:" in text
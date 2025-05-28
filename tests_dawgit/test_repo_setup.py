import sys
import os
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daw_git_gui import DAWGitApp

def test_git_init_creates_repo(tmp_path, qtbot):
    gui = DAWGitApp()
    gui.project_path = tmp_path
    os.chdir(tmp_path)  # Ensure working directory is the project path

    # Create a dummy Ableton file so init_git has something to track
    dummy_file = tmp_path / "dummy.als"
    dummy_file.write_text("Ableton dummy content")

    # Run Git initialization/setup
    gui.run_setup()

    # Assert .git folder is created indicating a Git repo was initialized
    assert (tmp_path / ".git").exists(), ".git folder should be created after Git init"
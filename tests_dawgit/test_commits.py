import os
import shutil
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from daw_git_gui import DAWGitApp

def test_auto_commit_creates_tag(tmp_path):
    os.chdir(tmp_path)
    shutil.copytree("tests_dawgit/test_fixtures/sample_repo", tmp_path, dirs_exist_ok=True)
    gui = DAWGitApp()
    gui.project_path = tmp_path
    gui.quick_auto_commit()
    assert (tmp_path / ".git").exists()

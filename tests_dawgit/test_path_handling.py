import os
from daw_git_gui import DAWGitApp

def test_path_change_and_clear(qtbot):
    app = DAWGitApp()
    original_path = app.project_path
    app.clear_saved_project()
    assert not app.settings_path.exists()
    app.project_path = original_path
    app.save_last_project_path()
    assert app.settings_path.exists()
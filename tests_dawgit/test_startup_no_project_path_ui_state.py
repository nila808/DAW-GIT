import pytest
from daw_git_gui import DAWGitApp
from ui_strings import STATUS_UNKNOWN, TAB_PROJECT_SETUP

def test_startup_no_project_path_ui_state(qtbot):
    app = DAWGitApp(project_path=None, build_ui=True)
    qtbot.addWidget(app)

    assert app.pages.currentWidget() == app.setup_page
    assert app.snapshot_status.text() == STATUS_UNKNOWN
    assert app.goto_setup_btn.text() == TAB_PROJECT_SETUP

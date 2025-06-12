import pytest
from daw_git_gui import DAWGitApp
from ui_strings import (
    STATUS_READY, 
    TAB_SNAPSHOT_BROWSER, 
    STATUS_BRANCH_TAKE
)


def test_startup_with_known_project_path(qtbot, tmp_path):
    als_file = tmp_path / "project.als"
    als_file.write_text("session")

    app = DAWGitApp(project_path=str(tmp_path), build_ui=True)
    qtbot.addWidget(app)

    assert app.project_path == tmp_path
    assert app.pages.currentWidget() == app.snapshot_page
    assert STATUS_BRANCH_TAKE.split(":")[0] in app.status_label.text()
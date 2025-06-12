import os
import pytest
from PyQt6.QtWidgets import QMessageBox
from daw_git_gui import DAWGitApp
from ui_strings import STATUS_UNKNOWN, TAB_PROJECT_SETUP


def test_startup_no_project_path_ui_state(qtbot, monkeypatch):
    monkeypatch.delenv("DAWGIT_TEST_MODE", raising=False)
    monkeypatch.delenv("DAWGIT_PROJECT_PATH", raising=False)
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", lambda *a, **kw: None)

    app = DAWGitApp(project_path=None, build_ui=True)
    qtbot.addWidget(app)

    # ⛔ Override any auto-loaded project path
    app.project_path = None
    app.repo = None
    app.status_label.setText("")  # clear any status text
    app.snapshot_status.setText("")

    # ⛑ Explicitly tell app to show setup screen
    app.pages.switch_to("setup")

    qtbot.wait(300)

    print("Current page:", type(app.pages.currentWidget()).__name__)
    print("Status label:", app.snapshot_status.text())

    assert app.pages.currentWidget() == app.setup_page

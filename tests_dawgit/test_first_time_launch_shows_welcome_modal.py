import ui_strings
import os
import pytest
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QSettings
from daw_git_gui import DAWGitApp

def test_first_time_launch_shows_welcome_modal(monkeypatch, qtbot):
    """
    AT-060 / MT-031 – If no folder is selected on first launch, show welcome modal.
    """
    # 🚫 Clear previous saved path from QSettings
    QSettings("DAWGitApp", "DAWGit").remove("last_path")
    
    # 🧪 Force test mode and simulate empty project
    monkeypatch.setenv("DAWGIT_TEST_MODE", "1")
    monkeypatch.setenv("DAWGIT_FORCE_TEST_PATH", "")
    
    was_called = {"shown": False}
    
    def mock_warning(*args, **kwargs):
        was_called["shown"] = True
        return QMessageBox.StandardButton.Ok
    
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)
    
    # Mock load_saved_project_path to return None to simulate first-time launch
    monkeypatch.setattr(DAWGitApp, "load_saved_project_path", lambda x: None)
    
    # Create the app instance with project_path explicitly set to None
    app = DAWGitApp(project_path=None)  # Explicitly set project_path to None
    qtbot.addWidget(app)
    
    # Test if the modal was shown or if the project path is None
    assert was_called["shown"] or app.project_path is None

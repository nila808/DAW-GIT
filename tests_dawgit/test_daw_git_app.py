import ui_strings
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QSettings  # Correctly import QSettings here
from pathlib import Path
from daw_git_gui import DAWGitApp  # Assuming DAWGitApp is the class you're testing
from tests_dawgit.test_helpers import create_test_project
from git import Repo
from ui_strings import (
    NO_REPO_LOADED_ERROR,
    PROJECT_SETUP_REQUIRED_MSG
)

# Assuming DAWGitApp is the class you're testing
@pytest.fixture
def mock_app(tmp_path):
    path, repo = create_test_project(tmp_path)
    app = DAWGitApp(project_path=str(path), build_ui=True)
    app.project_path = None  # No project path initially
    return app

def test_no_path_selection_resets_project(mock_app):
    print("[DEBUG] Clearing last project path...")
    settings = QSettings("DAWGitApp", "DAWGit")
    print(f"[DEBUG] Current last_project_path: {settings.value('last_project_path')}")
    settings.setValue("last_project_path", "")  # Explicitly set last_project_path to an empty string
    print("[DEBUG] Cleared last project path in settings.")
    # Mock QSettings value and setValue to ensure it gets called
    with patch.object(QSettings, 'value', return_value='/private/var/folders/.../VersionMarkerTest') as mock_value, \
         patch.object(QSettings, 'setValue') as mock_setValue:
    
        # Simulate selecting "No" in the modal
        with patch.object(mock_app, 'maybe_show_welcome_modal', return_value=None):
            mock_app.maybe_show_welcome_modal()
        
        # Explicitly call the method to clear the last path
        mock_app.clear_last_project_path()
        
        # Ensure the last path was cleared from settings
        mock_setValue.assert_called_once_with("last_project_path", "")  # Ensure it was called
        
        # Verify that no project path is loaded
        assert mock_app.project_path is None
        
        # Verify that the repo was not loaded (no initialization should have occurred)
        assert mock_app.repo is None
        
        # Verify that no further actions were taken
        # assert mock_app.status_label.text() == NO_REPO_LOADED_ERROR
        assert mock_app.status_label.text() == PROJECT_SETUP_REQUIRED_MSG
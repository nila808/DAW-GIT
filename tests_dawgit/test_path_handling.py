import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from daw_git_gui import DAWGitApp
from pathlib import Path
import pytest

class _DAWGitTestWrapper(DAWGitApp):
    def __init__(self, qtbot, test_path):
        # Register the widget with qtbot for proper PyQt testing lifecycle
        qtbot.addWidget(self)  
        self.project_path = test_path
        super().__init__(build_ui=True)  # Make sure UI is built

def test_path_change_and_clear(qtbot):
    fake_path = Path("/fake/path")
    app = _DAWGitTestWrapper(qtbot, fake_path)

    # Confirm that path_label exists on the UI
    assert hasattr(app, "path_label")

    # Test updating path_label text
    test_path = "/fake/path/to/project"
    app.path_label.setText(test_path)
    assert app.path_label.text() == test_path

    # Test clearing path_label text
    app.path_label.setText("")
    assert app.path_label.text() == ""

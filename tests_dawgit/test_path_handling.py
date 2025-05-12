from daw_git_gui import DAWGitApp
from pathlib import Path
import pytest

class _DAWGitTestWrapper(DAWGitApp):
    def __init__(self, qtbot, test_path):
        qtbot.addWidget(self)  # ✅ Registers the QApplication before QWidget is created
        self.project_path = test_path
        super().__init__()

def test_path_change_and_clear(qtbot):
    fake_path = Path("/fake/path")
    app = _DAWGitTestWrapper(qtbot, fake_path)

    assert hasattr(app, "path_label")

    test_path = "/fake/path/to/project"
    app.path_label.setText(test_path)
    assert app.path_label.text() == test_path

    app.path_label.setText("")
    assert app.path_label.text() == ""

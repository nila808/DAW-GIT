from unittest import mock
from daw_git_gui import DAWGitApp

def test_version_line_info(qtbot):
    app = DAWGitApp(build_ui=False)
    app.setup_ui()
    qtbot.addWidget(app)

    app.repo = mock.MagicMock()
    app.repo.active_branch.name = "version/0.0.1"

    app.update_version_line_label()  # <== Add this before checking the label
    label = app.version_line_label.text()
    assert "version/0.0.1" in label


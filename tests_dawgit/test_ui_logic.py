from daw_git_gui import DAWGitApp

def test_window_title(qtbot):
    app = DAWGitApp()
    assert app.windowTitle() == "DAW Git Version Control"
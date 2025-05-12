from daw_git_gui import DAWGitApp

def test_daw_file_readonly(qtbot):
    app = DAWGitApp(build_ui=False)
    qtbot.addWidget(app)

    # You need a valid commit SHA here
    dummy_sha = "HEAD"
    app.checkout_commit(commit_sha=dummy_sha)

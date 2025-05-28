def test_audio_and_midi_files_are_never_deleted(real_test_project):
    assert (real_test_project / "KICK.aif").exists()
    assert (real_test_project / "MIDI_1.mid").exists()
    assert (real_test_project / "session.als").exists()
    assert (real_test_project / "session.logicx").exists()


def test_real_project_files_present_on_load(real_test_project):
    daw_files = list(real_test_project.glob("*.als")) + list(real_test_project.glob("*.logicx"))
    audio_files = list(real_test_project.glob("*.aif")) + list(real_test_project.glob("*.wav"))
    midi_files = list(real_test_project.glob("*.mid"))

    assert daw_files, "No DAW session file found"
    assert audio_files, "No audio file found"
    assert midi_files, "No MIDI file found"


from daw_git_gui import DAWGitApp

def test_audio_midi_survive_commit_and_checkout(real_test_project, qtbot):
    # Init app
    app = DAWGitApp()
    app.project_path = str(real_test_project)
    app.init_git()
    app.bind_repo()

    qtbot.addWidget(app)
    qtbot.wait(100)

    # Commit a snapshot
    app.commit_changes("Real snapshot")
    qtbot.wait(100)

    sha = app.repo.head.commit.hexsha
    app.checkout_selected_commit(commit_sha=sha)
    qtbot.wait(100)

    # Ensure files still exist
    assert (real_test_project / "KICK.aif").exists(), "Audio file missing after checkout"
    assert (real_test_project / "MIDI_1.mid").exists(), "MIDI file missing after checkout"


def test_audio_midi_survive_branch_switch(real_test_project, qtbot):
    app = DAWGitApp()
    app.project_path = str(real_test_project)
    app.init_git()
    app.bind_repo()

    qtbot.addWidget(app)
    qtbot.wait(100)

    app.commit_changes("Base version")
    app.create_new_version_line("branch_audio_test")
    qtbot.wait(100)

    app.switch_branch("main")
    qtbot.wait(100)

    assert (real_test_project / "KICK.aif").exists(), "Audio file deleted after branch switch"
    assert (real_test_project / "MIDI_1.mid").exists(), "MIDI file deleted after branch switch"

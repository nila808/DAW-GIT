import ui_strings
from daw_git_gui import DAWGitApp
from tests_dawgit.test_helpers import create_test_project


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




def test_audio_midi_survive_commit_and_checkout(tmp_path, qtbot):
    from daw_git_gui import DAWGitApp
    from tests_dawgit.test_helpers import create_test_project

    path, repo = create_test_project(tmp_path)

    # Create audio + MIDI files
    (path / "KICK.aif").write_text("audio")
    (path / "MIDI_1.mid").write_text("midi")

    app = DAWGitApp(project_path=str(path), build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(100)

    app.commit_changes(commit_message="Add audio + midi")
    qtbot.wait(100)

    sha = app.repo.head.commit.hexsha
    app.checkout_selected_commit(commit_sha=sha)
    qtbot.wait(100)

    assert (path / "KICK.aif").exists(), "Audio file missing after checkout"
    assert (path / "MIDI_1.mid").exists(), "MIDI file missing after checkout"



def test_audio_midi_survive_branch_switch(real_test_project, qtbot, tmp_path):
    # Init app and repo
    path, repo = create_test_project(tmp_path)
    app = DAWGitApp(project_path=str(path), build_ui=True)
    app.project_path = str(real_test_project)
    app.init_git()
    app.bind_repo()
    qtbot.addWidget(app)
    qtbot.wait(100)

    # Save original content hashes (optional, stronger check)
    kick_path = real_test_project / "KICK.aif"
    midi_path = real_test_project / "MIDI_1.mid"
    original_kick = kick_path.read_bytes()
    original_midi = midi_path.read_bytes()

    # Commit + branch switch
    app.commit_changes("Base version")
    qtbot.wait(100)
    app.create_new_version_line("branch_audio_test")
    qtbot.wait(100)
    app.switch_branch("main")
    qtbot.wait(100)

    # Assert files still exist
    assert kick_path.exists(), "Audio file deleted after branch switch"
    assert midi_path.exists(), "MIDI file deleted after branch switch"

    # Assert content integrity (not just presence)
    assert kick_path.read_bytes() == original_kick, "Audio file content changed"
    assert midi_path.read_bytes() == original_midi, "MIDI file content changed"

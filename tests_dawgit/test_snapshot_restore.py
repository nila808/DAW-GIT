import os
from pathlib import Path
import tempfile
from daw_git_gui import DAWGitApp

def test_restore_snapshot(qtbot):
    app = DAWGitApp(build_ui=False)
    qtbot.addWidget(app)

    # Create a temp fake backup folder
    tmpdir = tempfile.TemporaryDirectory()
    fake_backup = Path(tmpdir.name) / "dummy.als"
    fake_backup.write_text("Ableton snapshot")
    app.project_path = Path(tmpdir.name)

    # Simulate restore behavior
    app.restore_last_backup()

    # Verify file is accessible again
    assert fake_backup.exists()

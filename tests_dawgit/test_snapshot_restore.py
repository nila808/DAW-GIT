import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
from pathlib import Path
import tempfile
import shutil
from daw_git_gui import DAWGitApp

def test_restore_snapshot(qtbot):
    app = DAWGitApp(build_ui=False)
    qtbot.addWidget(app)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "TestProject"
        project_path.mkdir()

        app.project_path = project_path

        # Create expected backup folder structure inside temp dir
        backup_folder = Path(tmpdir) / f"Backup_{project_path.name}_latest"
        backup_folder.mkdir(parents=True)

        # Place a dummy backup file inside backup folder
        backup_file = backup_folder / "dummy.als"
        backup_file.write_text("Ableton snapshot")

        # Now call restore (make sure your app looks in this backup folder)
        app.restore_last_backup()

        # After restore, file should exist in project folder
        restored_file = project_path / "dummy.als"
        assert restored_file.exists()
        assert restored_file.read_text() == "Ableton snapshot"

        # Clean up explicit since we used context manager (optional)
        shutil.rmtree(backup_folder, ignore_errors=True)

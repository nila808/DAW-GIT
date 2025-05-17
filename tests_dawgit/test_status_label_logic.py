import os
import time
from pathlib import Path

import pytest

from daw_git_gui import DAWGitApp

@pytest.fixture
def clean_daw_project(tmp_path):
    """Creates a dummy DAW project folder with a valid .als file and no dirty state."""
    project_dir = tmp_path / "TestProject"
    project_dir.mkdir()
    als_path = project_dir / "dummy.als"
    als_path.write_text("Ableton data")

    # ⏳ Set mtime to 2 minutes ago to avoid "recently modified" detection
    past = time.time() - 120
    os.utime(als_path, (past, past))

    return project_dir


def test_status_label_shows_clean_on_fresh_start(qtbot, clean_daw_project):
    time.sleep(2)  # Wait so .als timestamp is not seen as "recently modified"
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    label_text = app.status_label.text()
    assert "✅" in label_text or "🎧 On version line" in label_text
    assert "⚠️" not in label_text


def test_status_label_ignores_non_daw_files(qtbot, clean_daw_project):
    # Add a non-DAW file that would normally show up in git status
    (clean_daw_project / "Icon\r").write_text("junk")

    time.sleep(2)  # Prevent false positive from recent .als mod
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    assert not app.has_unsaved_changes(), "Non-DAW files should not trigger dirty state"
    label_text = app.status_label.text()
    assert "⚠️" not in label_text
    assert "🎧 On version line" in label_text


def test_status_label_detects_modified_als(qtbot, clean_daw_project):
    als_path = clean_daw_project / "dummy.als"
    als_path.write_text("original")

    # Set the modified time > 60 seconds ago so it starts clean
    past_time = time.time() - 120
    os.utime(als_path, (past_time, past_time))

    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    assert not app.has_unsaved_changes(), "Initial project state should be clean"

    # Modify the .als file to simulate unsaved changes
    als_path.write_text("modified data")

    # Re-check status
    app.update_status_label()

    assert app.has_unsaved_changes(), ".als modification should trigger dirty state"

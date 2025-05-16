import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path

@pytest.fixture
def clean_daw_project(tmp_path):
    """Creates a dummy DAW project folder with a valid .als file and no dirty state."""
    project_dir = tmp_path / "TestProject"
    project_dir.mkdir()
    (project_dir / "dummy.als").write_text("Ableton data")
    return project_dir

def test_status_label_shows_clean_on_fresh_start(qtbot, clean_daw_project):
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    label_text = app.status_label.text()
    assert "✅" in label_text or "🎧 On version line" in label_text
    assert "⚠️" not in label_text

def test_status_label_ignores_non_daw_files(qtbot, clean_daw_project):
    # Add a non-DAW file that would normally show up in git status
    (clean_daw_project / "Icon\r").write_text("junk")
    
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    assert not app.has_unsaved_changes(), "Non-DAW files should not trigger dirty state"
    label_text = app.status_label.text()
    assert "⚠️" not in label_text
    assert "🎧 On version line" in label_text

def test_status_label_detects_modified_als(qtbot, clean_daw_project):
    als_path = clean_daw_project / "dummy.als"
    als_path.write_text("original")

    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    # ✅ Ensure the initial state is clean
    assert not app.has_unsaved_changes(), "Initial project state should be clean"

    # 🔥 Modify the .als file after app is launched
    als_path.write_text("modified data")

    # 🧪 Trigger status re-check
    app.update_status_label()

    # ✅ Assert that the dirty state is detected
    assert app.has_unsaved_changes(), ".als modification should trigger dirty state"

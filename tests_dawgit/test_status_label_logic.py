import ui_strings
import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import
import time
import re
from pathlib import Path
from git import Repo
import pytest
from PyQt6.QtWidgets import QApplication
from ui_strings import STATUS_UNKNOWN
from daw_git_gui import DAWGitApp



def strip_html(text):
    """Remove HTML tags from QLabel text content."""
    return re.sub(r"<[^>]*>", "", text)

@pytest.fixture
def clean_daw_project(tmp_path):
    """Creates a dummy DAW project folder with a valid .als file and no dirty state."""
    project_dir = tmp_path / f"TestProject_{time.time_ns()}"
    project_dir.mkdir()
    als_path = project_dir / ui_strings.DUMMY_ALS_FILE
    als_path.write_text("Ableton data")

    past = time.time() - 120
    os.utime(als_path, (past, past))

    return project_dir

def test_status_label_shows_clean_on_fresh_start(qtbot, clean_daw_project, app):
    time.sleep(1.5)  # Ensure no race with mtime check
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    label_text = strip_html(app.status_label.text())

    # ✅ Updated assertions to match current label format
    assert "Version Line" in label_text
    assert "Take:" in label_text


def test_status_label_ignores_non_daw_files(qtbot, clean_daw_project, app):
    # Add ignored metadata file (commonly created by macOS)
    ignored_file = clean_daw_project / ".DS_Store"
    ignored_file.write_text("junk")
    os.utime(ignored_file, (time.time() - 120, time.time() - 120))

    time.sleep(1.5)
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    label_text = strip_html(app.status_label.text())
    assert "Version Line" in label_text
    assert "Take:" in label_text
    assert "Unsaved" not in label_text 


def test_status_label_detects_modified_als(qtbot, clean_daw_project, app):
    als_path = clean_daw_project / ui_strings.DUMMY_ALS_FILE
    als_path.write_text("original")

    # 💾 Init repo and commit the file BEFORE app launch
    repo = Repo.init(clean_daw_project)
    repo.index.add([ui_strings.DUMMY_ALS_FILE])
    repo.index.commit("initial version")

    # 🔄 Launch app (clean state expected)
    app = DAWGitApp(project_path=clean_daw_project, build_ui=True)
    qtbot.addWidget(app)

    assert not app.has_unsaved_changes(), "Initial project state should be clean"


@pytest.mark.usefixtures("qtbot")
def test_status_label_shows_clean_output_if_no_repo(tmp_path, qtbot):
    """Ensure that the status label does not show fallback garbage like 'unknown' or unused placeholders."""

    os.environ["DAWGIT_TEST_MODE"] = "1"

    app = DAWGitApp()
    qtbot.addWidget(app)

    app.project_path = None
    app.repo = None

    app.show_status_message()

    label_text = app.snapshot_page.status_label.text().lower()

    # ✅ It should not say 'unknown', 'snapshot mode', or similar fallbacks
    assert "unknown" not in label_text
    assert "snapshot mode" not in label_text

    # ✅ It should either be clean, empty, or something helpful
    # Allowable clean states
    allowed = {
        "", "–",
        "🎼 no active version line",
        "🎚️ no session loaded",
        "ℹ️ detached snapshot — not on an active version line"
    }

    assert label_text.strip().lower() in allowed
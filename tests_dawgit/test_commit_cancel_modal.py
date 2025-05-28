import pytest
from daw_git_gui import DAWGitApp
from pathlib import Path
from PyQt6.QtWidgets import QInputDialog

@pytest.fixture
def daw_project_with_als(tmp_path):
    """Creates a DAW project folder with a valid .als file."""
    project_dir = tmp_path / "CommitCancelTest"
    project_dir.mkdir()
    (project_dir / "dummy.als").write_text("Ableton content")
    return project_dir

def test_commit_cancel_does_not_change_repo(monkeypatch, qtbot, daw_project_with_als):
    app = DAWGitApp(project_path=daw_project_with_als, build_ui=True)
    qtbot.addWidget(app)

    app.init_git()
    initial_commit_count = len(list(app.repo.iter_commits()))

    # Monkeypatch QInputDialog.getText to simulate the Cancel button clicked
    def fake_get_text(*args, **kwargs):
        return ("", False)  # Cancel pressed, so no commit message

    monkeypatch.setattr(QInputDialog, "getText", fake_get_text)

    result = app.commit_changes()

    # When commit is cancelled, commit_changes() returns None or dict with error status
    assert result is None or (isinstance(result, dict) and result.get("status") == "error")

    final_commit_count = len(list(app.repo.iter_commits()))
    assert final_commit_count == initial_commit_count, "No new commit should be created when commit is cancelled"

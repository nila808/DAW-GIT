import ui_strings
import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import
import pytest
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QApplication
from pathlib import Path

@pytest.fixture
def app(qtbot, tmp_path):
    # Create fake project with .als file
    project_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    project_path.mkdir()
    (project_path / "track.als").write_text("test")

    # Initialize app
    test_app = DAWGitApp(str(project_path))
    qtbot.addWidget(test_app)

    # Simulate Git setup
    test_app.init_git()
    test_app.load_commit_history()

    return test_app

def test_full_snapshot_flow(app, qtbot):

    # Create a commit — modify .als file to ensure diff
    als_path = app.project_path / "track.als"
    als_path.write_text("updated snapshot content")  # ✅ trigger change

    # Create a commit
    app.pages.switch_to("commit")
    app.commit_page.commit_message.setPlainText("Initial snapshot")

    result = app.commit_changes("Initial snapshot")
    assert result["status"] == "success"

    # Reload and reselect HEAD row safely
    app.load_commit_history()

    # Find HEAD SHA and locate matching row
    sha = app.repo.head.commit.hexsha[:7]
    for row in range(app.history_table.rowCount()):
        item = app.history_table.item(row, 2)
        if item and sha == item.text():
            app.history_table.selectRow(row)
            break

    # Now perform checkout
    print(">>> COMMIT SHA:", app.repo.head.commit.hexsha)
    print(">>> Selected row SHA:", app.history_table.item(row, 2).text())
    result = app.checkout_selected_commit()
    if result["status"] == "noop":
        assert result["message"].startswith("Already on this commit")
    else:
        assert result["status"] == "success"


    # Tag it and ensure the tag shows
    app.assign_commit_role(app.current_commit_id, "Main Mix")
    role = app.commit_roles.get(app.current_commit_id)
    assert role == "Main Mix"

    # Reload history to confirm role appears in table
    app.load_commit_history()
    found_role = app.history_table.item(0, 1).text()
    assert found_role == "Main Mix"

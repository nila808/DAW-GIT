import os
import pytest
from daw_git_gui import DAWGitApp

@pytest.mark.usefixtures("qtbot")
def test_redirect_to_setup_if_no_project_path(qtbot):
    # ❌ Undo what conftest.py set
    if "DAWGIT_FORCE_TEST_PATH" in os.environ:
        del os.environ["DAWGIT_FORCE_TEST_PATH"]

    os.environ["DAWGIT_TEST_MODE"] = "1"

    app = DAWGitApp(project_path=None)
    qtbot.addWidget(app)

    assert app.pages.currentWidget() == app.setup_page
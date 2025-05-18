import pytest
from daw_git_gui import DAWGitApp
from PyQt6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

@pytest.fixture
def app(qtbot: QtBot):
    test_app = DAWGitApp(build_ui=False)
    qtbot.addWidget(test_app)
    return test_app

def test_placeholder(app):
    assert app is not None

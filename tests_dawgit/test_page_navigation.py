from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt


def test_nav_buttons_switch_pages(qtbot, app):
    qtbot.mouseClick(app.goto_commit_btn, Qt.MouseButton.LeftButton)
    assert app.pages.currentWidget() == app.commit_page

    qtbot.mouseClick(app.goto_branch_btn, Qt.MouseButton.LeftButton)
    assert app.pages.currentWidget() == app.branch_page

    qtbot.mouseClick(app.goto_snapshots_btn, Qt.MouseButton.LeftButton)
    assert app.pages.currentWidget() == app.snapshot_page

    qtbot.mouseClick(app.goto_setup_btn, Qt.MouseButton.LeftButton)
    assert app.pages.currentWidget() == app.setup_page
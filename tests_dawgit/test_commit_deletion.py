from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from daw_git_gui import DAWGitApp

def test_delete_commit(qtbot):
    app = DAWGitApp(build_ui=False)
    qtbot.addWidget(app)

    # Inject a fake history table
    app.history_table = QTableWidget(1, 3)
    fake_id = "abcd1234"
    fake_msg = "Test commit to delete"

    item_id = QTableWidgetItem("FakeID")
    item_id.setToolTip(fake_id)
    item_msg = QTableWidgetItem(fake_msg)
    app.history_table.setItem(0, 1, item_id)
    app.history_table.setItem(0, 2, item_msg)
    app.history_table.selectRow(0)

    # Call method
    app.delete_selected_commit()

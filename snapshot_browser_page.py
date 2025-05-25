from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QLineEdit, QHBoxLayout, QTableWidgetItem, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt

class SnapshotBrowserPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Title/Header
        self.title_label = QLabel("🎧 Snapshot Browser")
        layout.addWidget(self.title_label)

        # 📜 Version History Table
        self.commit_table = QTableWidget()
        layout.addWidget(self.commit_table)
        self.commit_table.setColumnCount(9)
        self.commit_table.setHorizontalHeaderLabels([
            "#", "Role", "Commit ID", "Message", "Branch", "DAW", "Files", "Tags", "Date"
        ])

        # Commit message input
        self.commit_message_input = QLineEdit()
        self.commit_message_input.setPlaceholderText("Enter snapshot message...")
        layout.addWidget(self.commit_message_input)

        # Status label
        self.status_label = QLabel("📦 Ready")
        layout.addWidget(self.status_label)

        # Stretch to bottom
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


    def highlight_row_by_sha(self, sha: str):
        for row in range(self.commit_table.rowCount()):
            item = self.commit_table.item(row, 2)  # Column 2 = Commit ID
            if item and item.toolTip() == sha:
                self.commit_table.selectRow(row)
                self.commit_table.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)
                for col in range(self.commit_table.columnCount()):
                    cell = self.commit_table.item(row, col)
                    if cell:
                        cell.setBackground(Qt.GlobalColor.green)
                break

    def clear_table(self):
        self.commit_table.setRowCount(0)
        self.commit_table.clearSelection()

    def show_placeholder_row(self):
        self.commit_table.setRowCount(0)
        self.commit_table.insertRow(0)
        placeholders = ["–"] * 9
        for col, text in enumerate(placeholders):
            self.commit_table.setItem(0, col, QTableWidgetItem(text))



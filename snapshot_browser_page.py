from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QLineEdit, QHBoxLayout, QTableWidgetItem, QSpacerItem, QSizePolicy,
    QTextEdit
)
from PyQt6.QtCore import Qt

class SnapshotBrowserPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent  # Safe access to DAWGitApp
        layout = QVBoxLayout(self)

        # 🎧 Header
        self.title_label = QLabel("🎧 Snapshot Browser")
        layout.addWidget(self.title_label)

        # 📜 Commit History Table
        self.commit_table = QTableWidget()
        self.commit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.commit_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.commit_table)
        self.commit_table.setColumnCount(9)
        self.commit_table.setHorizontalHeaderLabels([
            "#", "Role", "Commit ID", "Message", "Branch", "DAW", "Files", "Tags", "Date"
        ])
        self.commit_table.setSortingEnabled(True)
        self.commit_table.sortItems(0, Qt.SortOrder.AscendingOrder)

        self.commit_table.setAlternatingRowColors(True)
        self.commit_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #b3d9ff;  /* light blue highlight */
            }
        """)
        self.commit_table.sortItems(8, Qt.SortOrder.DescendingOrder)

        # 📦 Status
        self.status_label = QLabel("📦 Ready")
        layout.addWidget(self.status_label)

        # 📥 Load + Info
        self.load_snapshot_btn = QPushButton("🎧 Load This Snapshot")
        self.load_snapshot_btn.setToolTip("Load this version of your project safely")
        if self.app and hasattr(self.app, "load_snapshot_clicked"):
            self.load_snapshot_btn.clicked.connect(self.app.load_snapshot_clicked)
        layout.addWidget(self.load_snapshot_btn)

        self.where_am_i_btn = QPushButton("📍 Where Am I?")
        self.where_am_i_btn.setToolTip("Show current snapshot version")
        if self.app and hasattr(self.app, "show_current_commit"):
            self.where_am_i_btn.clicked.connect(self.app.show_current_commit)
        layout.addWidget(self.where_am_i_btn)

        # 🧭 Snapshot Action Bar (Quick Save + Tags)
        action_row = QHBoxLayout()

        self.quick_commit_btn = QPushButton("💾 Quick Save")
        self.quick_commit_btn.setToolTip("Save a snapshot using the most recent commit message")
        if self.app and hasattr(self.app, "quick_commit"):
            self.quick_commit_btn.clicked.connect(self.app.quick_commit)

        self.quick_tag_main_btn = QPushButton("🎼 Save Snapshot as New Version")
        self.quick_tag_main_btn.setToolTip("Create a new version line from this snapshot.")
        if self.app and hasattr(self.app, "tag_main_mix"):
            self.quick_tag_main_btn.clicked.connect(self.app.tag_main_mix)

        self.quick_tag_creative_btn = QPushButton("🎨 Creative")
        self.quick_tag_creative_btn.setToolTip("Tag the selected snapshot as a creative take")
        if self.app and hasattr(self.app, "tag_creative_take"):
            self.quick_tag_creative_btn.clicked.connect(self.app.tag_creative_take)

        self.quick_tag_alt_btn = QPushButton("🎛️ Alt Mix")
        self.quick_tag_alt_btn.setToolTip("Tag the selected snapshot as an alternate version")
        if self.app and hasattr(self.app, "tag_alt_mix"):
            self.quick_tag_alt_btn.clicked.connect(self.app.tag_alt_mix)

        self.open_commit_page_btn = QPushButton("✏️ Open Commit Panel")
        self.open_commit_page_btn.setToolTip("Open full snapshot editor")
        if self.app and hasattr(self.app, "pages"):
            self.open_commit_page_btn.clicked.connect(lambda: self.app.pages.switch_to("commit"))

        # 🧼 Only add buttons that exist
        for btn in [
            self.quick_commit_btn,
            self.quick_tag_main_btn if hasattr(self, "quick_tag_main_btn") else None,
            self.quick_tag_creative_btn if hasattr(self, "quick_tag_creative_btn") else None,
            self.quick_tag_alt_btn if hasattr(self, "quick_tag_alt_btn") else None,
            self.open_commit_page_btn
        ]:
            if btn:  # skip None safely
                action_row.addWidget(btn)

        layout.addLayout(action_row)

        # Spacer
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



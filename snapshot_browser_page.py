from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QLineEdit, QHBoxLayout, QTableWidgetItem, QSpacerItem, QSizePolicy,
    QTextEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor


from ui_strings import (
    RETURN_TO_LATEST_BTN, 
    TOOLTIP_RETURN_TO_LATEST, 
    TOOLTIP_LOAD_VERSION_SAFELY,
    TOOLTIP_SHOW_CURRENT_VERSION,   
    TOOLTIP_SAVE_WITH_LAST_MESSAGE, 
    TOOLTIP_TAG_CREATIVE,
    TOOLTIP_TAG_ALT_MIX,
    TOOLTIP_OPEN_COMMIT_PANEL,
    BTN_LOAD_SNAPSHOT, 
    BTN_WHERE_AM_I, 
    BTN_QUICK_SAVE, 
    BTN_MAIN_MIX, 
    BTN_CREATIVE_TAKE, 
    BTN_ALT_MIX, 
    BTN_OPEN_COMMIT_PANEL,
    SNAPSHOT_BROWSER_TITLE,
    SESSION_LABEL_UNKNOWN,
    TOOLTIP_TAG_MAIN_MIX, 
    TABLE_HEADER_TAKE_ID,
    TABLE_HEADER_TAKE_NOTES,
    TABLE_HEADER_SESSION_LINE, 
    STATUS_READY, 
    BTN_TAG_CUSTOM_LABEL, 
    ROLE_CUSTOM_TAG_TOOLTIP
)

class SnapshotBrowserPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent  # Safe access to DAWGitApp
        layout = QVBoxLayout(self)

        # 🎧 Header
        self.title_label = QLabel(SNAPSHOT_BROWSER_TITLE)
        layout.addWidget(self.title_label)

        # # 📢 Session Label (shows current branch + version info)
        self.version_line_label = QLabel(SESSION_LABEL_UNKNOWN)
        self.version_line_label.setObjectName("versionLineLabel")
        layout.addWidget(self.version_line_label)

        # 📜 Commit History Table
        self.commit_table = QTableWidget()
        self.commit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.commit_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.commit_table)
        self.commit_table.setColumnCount(9)
        self.commit_table.setHorizontalHeaderLabels([
            "#", "Role", TABLE_HEADER_TAKE_ID, TABLE_HEADER_TAKE_NOTES,
            TABLE_HEADER_SESSION_LINE, "DAW", "Files", "Tags", "Date"
        ])
        self.commit_table.setSortingEnabled(True)
        self.commit_table.sortItems(0, Qt.SortOrder.AscendingOrder)

        self.commit_table.setAlternatingRowColors(True)
        # self.commit_table.setStyleSheet("""
        #     QTableWidget::item:selected {
        #         background-color: #b3d9ff;  /* light blue highlight */
        #     }
        # """)
        self.commit_table.sortItems(8, Qt.SortOrder.DescendingOrder)

        # 📦 Status
        self.status_label = QLabel(STATUS_READY)
        layout.addWidget(self.status_label)

        # 📥 Load + Info
        self.load_snapshot_btn = QPushButton(BTN_LOAD_SNAPSHOT)
        self.load_snapshot_btn.setToolTip(TOOLTIP_LOAD_VERSION_SAFELY)
        if self.app and hasattr(self.app, "load_snapshot_clicked"):
            self.load_snapshot_btn.clicked.connect(self.app.load_snapshot_clicked)
        layout.addWidget(self.load_snapshot_btn)

        self.where_am_i_btn = QPushButton(BTN_WHERE_AM_I)
        self.where_am_i_btn.setToolTip(TOOLTIP_SHOW_CURRENT_VERSION)
        if self.app and hasattr(self.app, "show_current_commit"):
            self.where_am_i_btn.clicked.connect(self.app.show_current_commit)
        layout.addWidget(self.where_am_i_btn)

        self.return_to_latest_btn = QPushButton(RETURN_TO_LATEST_BTN)
        self.return_to_latest_btn.setToolTip(TOOLTIP_RETURN_TO_LATEST)
        if self.app and hasattr(self.app, "return_to_latest_clicked"):
            self.return_to_latest_btn.clicked.connect(self.app.return_to_latest_clicked)
        layout.addWidget(self.return_to_latest_btn)

        # 🧭 Snapshot Action Bar (Quick Save + Tags)
        action_row = QHBoxLayout()

        self.quick_commit_btn = QPushButton(BTN_QUICK_SAVE)
        self.quick_commit_btn.setToolTip(TOOLTIP_SAVE_WITH_LAST_MESSAGE)
        self.quick_commit_btn.clicked.connect(lambda: self.app.quick_commit())

        self.quick_tag_main_btn = QPushButton(BTN_MAIN_MIX)
        self.quick_tag_main_btn.setToolTip(TOOLTIP_TAG_MAIN_MIX)
        self.quick_tag_main_btn.clicked.connect(lambda: self.app.tag_main_mix())

        self.quick_tag_creative_btn = QPushButton(BTN_CREATIVE_TAKE)
        self.quick_tag_creative_btn.setToolTip(TOOLTIP_TAG_CREATIVE)
        self.quick_tag_creative_btn.clicked.connect(lambda: self.app.tag_creative_take())

        self.quick_tag_alt_btn = QPushButton(BTN_ALT_MIX)
        self.quick_tag_alt_btn.setToolTip(TOOLTIP_TAG_ALT_MIX)
        self.quick_tag_alt_btn.clicked.connect(lambda: self.app.tag_alt_mix())

        self.tag_custom_btn = QPushButton(BTN_TAG_CUSTOM_LABEL)
        self.tag_custom_btn.setToolTip(ROLE_CUSTOM_TAG_TOOLTIP)
        self.tag_custom_btn.clicked.connect(self.app.tag_custom_label)
    

        self.open_commit_page_btn = QPushButton(BTN_OPEN_COMMIT_PANEL)
        self.open_commit_page_btn.setToolTip(TOOLTIP_OPEN_COMMIT_PANEL)
        self.open_commit_page_btn.clicked.connect(lambda: self.app.pages.switch_to("commit"))


        for btn in [
            self.quick_commit_btn,
            self.quick_tag_main_btn,
            self.quick_tag_creative_btn,
            self.quick_tag_alt_btn,
            self.tag_custom_btn,
            self.open_commit_page_btn
        ]:
            action_row.addWidget(btn)

        layout.addLayout(action_row)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Fix table highlight colors for better contrast
        
        # palette = self.commit_table.palette()
        # palette.setColor(QPalette.ColorRole.Highlight, QColor("#cceedd"))           # pale soft green
        # palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))     # dark text for contrast
        # self.commit_table.setPalette(palette)


    def update_return_to_latest_visibility(self):
        if self.app and self.app.repo:
            is_detached = self.app.repo.head.is_detached
            self.return_to_latest_btn.setVisible(is_detached)
        else:
            self.return_to_latest_btn.setVisible(False)
    

    def highlight_row_by_sha(self, sha: str):
        for row in range(self.commit_table.rowCount()):
            item = self.commit_table.item(row, 2)  # Column 2 = Commit ID
            if item and item.toolTip() == sha:
                self.commit_table.selectRow(row)
                self.commit_table.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)
                # ==== Inline Python styling ========
                # for col in range(self.commit_table.columnCount()):
                #     cell = self.commit_table.item(row, col)
                #     if cell:
                #         cell.setBackground(Qt.GlobalColor.green)
                # break


    def clear_table(self):
        self.commit_table.setRowCount(0)
        self.commit_table.clearSelection()


    def show_placeholder_row(self):
        self.commit_table.setRowCount(0)
        self.commit_table.insertRow(0)
        placeholders = ["–"] * 9
        for col, text in enumerate(placeholders):
            self.commit_table.setItem(0, col, QTableWidgetItem(text))



from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from ui_strings import (
    BTN_START_TRACKING,
    BTN_LOAD_ALT_SESSION,
    BTN_CHANGE_PROJECT_FOLDER,
    BTN_CLEAR_SAVED_PROJECT,
    BTN_EXPORT_SNAPSHOT,
    BTN_IMPORT_SNAPSHOT,
    BTN_RESTORE_BACKUP,
    BTN_CONNECT_REMOTE_REPO, 
    CLICK_TO_OPEN_IN_FINDER_TOOLTIP, 
    SETUP_REMOTE_TOOLTIP
)



class ProjectSetupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent
        layout = QVBoxLayout(self)

        # 🎵 Project Setup Header
        self.title_label = QLabel("🎵 Project Setup")
        layout.addWidget(self.title_label)

        # 📁 Project Display Label
        self.app.project_label = QLabel()
        self.app.project_label.setObjectName("project_label")
        self.app.project_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.app.project_label.setOpenExternalLinks(True)
        self.app.project_label.setToolTip(CLICK_TO_OPEN_IN_FINDER_TOOLTIP)
        self.app.project_label.setWordWrap(True)
        layout.addWidget(self.app.project_label)

        # 🔍 Hidden Path Label (used in test assertions or debug)
        self.app.path_label = QLabel(str(self.app.project_path))
        self.app.path_label.setVisible(False)
        layout.addWidget(self.app.path_label)

        # 🛠️ Setup + Load
        self.setup_btn = QPushButton(BTN_START_TRACKING)
        self.load_alt_btn = QPushButton(BTN_LOAD_ALT_SESSION)

        setup_row = QHBoxLayout()
        setup_row.addWidget(self.setup_btn)
        setup_row.addWidget(self.load_alt_btn)
        layout.addLayout(setup_row)

        self.setup_btn.clicked.connect(self.app.run_setup)
        self.load_alt_btn.clicked.connect(self.app.select_folder_clicked)

        # 📁 Folder controls
        folder_controls = QHBoxLayout()
        self.change_folder_btn = QPushButton(BTN_CHANGE_PROJECT_FOLDER)
        self.clear_project_btn = QPushButton(BTN_CLEAR_SAVED_PROJECT)
        folder_controls.addWidget(self.change_folder_btn)
        folder_controls.addWidget(self.clear_project_btn)
        layout.addLayout(folder_controls)

        self.change_folder_btn.clicked.connect(self.app.change_project_folder)
        self.clear_project_btn.clicked.connect(self.app.clear_saved_project)

        # 📦 Snapshot export/import
        snapshot_controls = QHBoxLayout()
        self.export_btn = QPushButton(BTN_EXPORT_SNAPSHOT)
        self.import_btn = QPushButton(BTN_IMPORT_SNAPSHOT)
        self.restore_btn = QPushButton(BTN_RESTORE_BACKUP)
        snapshot_controls.addWidget(self.export_btn)
        snapshot_controls.addWidget(self.import_btn)
        snapshot_controls.addWidget(self.restore_btn)
        layout.addLayout(snapshot_controls)

        self.remote_checkbox = QCheckBox("Push to remote after snapshot")
        layout.addWidget(self.remote_checkbox)

        self.connect_remote_btn = QPushButton(BTN_CONNECT_REMOTE_REPO)
        self.connect_remote_btn.setToolTip(SETUP_REMOTE_TOOLTIP)
        self.connect_remote_btn.clicked.connect(self.app.connect_to_remote_repo)

        layout.addWidget(self.connect_remote_btn)

        self.export_btn.clicked.connect(self.app.export_snapshot)
        self.import_btn.clicked.connect(self.app.import_snapshot)
        self.restore_btn.clicked.connect(self.app.restore_last_backup)

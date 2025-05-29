from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt

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
        self.app.project_label.setToolTip("Click to open in Finder")
        self.app.project_label.setWordWrap(True)
        layout.addWidget(self.app.project_label)

        # 🔍 Hidden Path Label (used in test assertions or debug)
        self.app.path_label = QLabel(str(self.app.project_path))
        self.app.path_label.setVisible(False)
        layout.addWidget(self.app.path_label)

        # 🛠️ Setup + Load
        self.setup_btn = QPushButton("Start Tracking")
        self.load_alt_btn = QPushButton("Load Alternate Session")

        setup_row = QHBoxLayout()
        setup_row.addWidget(self.setup_btn)
        setup_row.addWidget(self.load_alt_btn)
        layout.addLayout(setup_row)

        self.setup_btn.clicked.connect(self.app.run_setup)
        self.load_alt_btn.clicked.connect(self.app.select_folder_clicked)

        # 📁 Folder controls
        folder_controls = QHBoxLayout()
        self.change_folder_btn = QPushButton("Change Project Folder")
        self.clear_project_btn = QPushButton("Clear Saved Project")
        folder_controls.addWidget(self.change_folder_btn)
        folder_controls.addWidget(self.clear_project_btn)
        layout.addLayout(folder_controls)

        self.change_folder_btn.clicked.connect(self.app.change_project_folder)
        self.clear_project_btn.clicked.connect(self.app.clear_saved_project)

        # 📦 Snapshot export/import
        snapshot_controls = QHBoxLayout()
        self.export_btn = QPushButton("Export Snapshot")
        self.import_btn = QPushButton("Import Snapshot")
        self.restore_btn = QPushButton("Restore Last Backup")
        snapshot_controls.addWidget(self.export_btn)
        snapshot_controls.addWidget(self.import_btn)
        snapshot_controls.addWidget(self.restore_btn)
        layout.addLayout(snapshot_controls)

        self.remote_checkbox = QCheckBox("Push to remote after snapshot")
        layout.addWidget(self.remote_checkbox)

        self.connect_remote_btn = QPushButton("🔗 Connect to Remote Repo")
        self.connect_remote_btn.setToolTip("Set up a remote Git URL (e.g. GitHub)")
        self.connect_remote_btn.clicked.connect(self.app.connect_to_remote_repo)

        layout.addWidget(self.connect_remote_btn)

        self.export_btn.clicked.connect(self.app.export_snapshot)
        self.import_btn.clicked.connect(self.app.import_snapshot)
        self.restore_btn.clicked.connect(self.app.restore_last_backup)

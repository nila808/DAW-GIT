from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daw_git_gui import DAWGitApp

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from ui_strings import SNAPSHOT_EDIT_BLOCK_TOOLTIP


class CommitPage(QWidget):
    def __init__(self, app=None, parent=None):
        super().__init__(parent)
        self.app = app  # 🔗 Store main app reference


        layout = QVBoxLayout(self)

        # 🎼 Title
        self.title_label = QLabel("📥 Commit Snapshot")
        layout.addWidget(self.title_label)

        self.snapshot_status_label = QLabel("")
        self.snapshot_status_label.setObjectName("snapshotStatusLabel")
        self.snapshot_status_label.setText(SNAPSHOT_EDIT_BLOCK_TOOLTIP)
        self.snapshot_status_label.setToolTip(SNAPSHOT_EDIT_BLOCK_TOOLTIP)

        layout.addWidget(self.snapshot_status_label)

        # 📝 Commit message
        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("Describe what changed in this snapshot")
        self.commit_message.setFixedHeight(80)
        layout.addWidget(self.commit_message)

        # 🧠 Auto-save toggle
        self.auto_save_toggle = QCheckBox("Enable Auto-Snapshot")
        layout.addWidget(self.auto_save_toggle)
        self.auto_save_toggle.stateChanged.connect(self.toggle_auto_commit)

        # 🎯 Return to Latest button
        self.return_to_latest_btn = QPushButton("🎯 Return to Latest")
        self.return_to_latest_btn.setToolTip("Return to the most recent snapshot on your version line")
        if parent and hasattr(parent, "return_to_latest_clicked"):
            self.return_to_latest_btn.clicked.connect(parent.return_to_latest_clicked)
        layout.addWidget(self.return_to_latest_btn)

        # 💾 Commit button
        self.commit_button = QPushButton("💾 Commit Now")
        layout.addWidget(self.commit_button)
        self.commit_button.clicked.connect(self.commit_snapshot)

        self.btn_version_main = QPushButton("Main Mix")
        self.btn_version_creative = QPushButton("Creative")
        self.btn_version_alt = QPushButton("Alt Mix")


        # 🏷️ Tagging Buttons
        tag_layout = QHBoxLayout()
        self.tag_main_btn = QPushButton("🌟 Mark as Final Mix")
        self.tag_creative_btn = QPushButton("🎨 Mark as Creative Version")
        self.tag_alt_btn = QPushButton("🎛️ Mark as Alternate Mix")
        self.tag_custom_btn = QPushButton("✏️ Add Custom Tag")
        tag_layout.addWidget(self.tag_main_btn)
        tag_layout.addWidget(self.tag_creative_btn)
        tag_layout.addWidget(self.tag_alt_btn)
        tag_layout.addWidget(self.tag_custom_btn)
        layout.addLayout(tag_layout)

        self.tag_main_btn.clicked.connect(self.app.tag_main_mix)
        self.tag_creative_btn.clicked.connect(self.app.tag_creative_take)
        self.tag_alt_btn.clicked.connect(self.app.tag_alt_mix)
        self.tag_custom_btn.clicked.connect(self.app.tag_custom_label)

        # 🎧 Open in DAW button
        self.open_in_daw_btn = QPushButton("🎧 Open This Version in Ableton")
        self.open_in_daw_btn.setToolTip("Launch Ableton with the checked-out snapshot")
        self.open_in_daw_btn.setVisible(False)  # Hidden by default
        layout.addWidget(self.open_in_daw_btn)

        # Connect to app method
        self.open_in_daw_btn.clicked.connect(self.app.open_in_daw)


        # 🎯 Status label
        self.status_label = QLabel("📦 Ready to commit")
        layout.addWidget(self.status_label)

        # Link buttons to app for timer updates
        if hasattr(self.app, "commit_button") is False:
            self.app.commit_button = self.commit_button
        if hasattr(self.app, "auto_save_toggle") is False:
            self.app.auto_save_toggle = self.auto_save_toggle


    def update_snapshot_editing_state(self):
        """
        Update snapshot status label and tooltips based on HEAD state.
        """
        if self.app and self.app.repo and self.app.repo.head.is_detached:
            self.snapshot_status_label.setText(SNAPSHOT_EDIT_BLOCK_TOOLTIP)
            self.snapshot_status_label.setToolTip(SNAPSHOT_EDIT_BLOCK_TOOLTIP)
        else:
            self.snapshot_status_label.setText("")
            self.snapshot_status_label.setToolTip("")


    def commit_snapshot(self):
        message = self.commit_message.toPlainText().strip()
        if not message:
            self.status_label.setText("❌ Commit message is required.")
            return

        result = self.app.commit_changes(commit_message=message)
        if result["status"] == "success":
            self.status_label.setText(f"✅ Committed: {result['sha'][:7]}")
            self.commit_message.clear()
        else:
            error_msg = result.get("message", "Unknown error.")
            self.status_label.setText(f"❌ Couldn’t save snapshot:\n{error_msg}")
            self.commit_message.clear()  # ✅ Always clear after failure


    def toggle_auto_commit(self, state):
        if hasattr(self.app, "handle_auto_save_toggle"):
            self.app.handle_auto_save_toggle(state)

    
    def set_commit_controls_enabled(self, enabled: bool, tooltip: str = ""):
        self.commit_button.setEnabled(enabled)
        self.commit_button.setToolTip(tooltip)

        self.commit_message.setEnabled(enabled)
        self.commit_message.setToolTip(tooltip)

        self.tag_main_btn.setEnabled(enabled)
        self.tag_main_btn.setToolTip(tooltip)

        self.tag_creative_btn.setEnabled(enabled)
        self.tag_creative_btn.setToolTip(tooltip)

        self.tag_alt_btn.setEnabled(enabled)
        self.tag_alt_btn.setToolTip(tooltip)

        self.tag_custom_btn.setEnabled(enabled)
        self.tag_custom_btn.setToolTip(tooltip)
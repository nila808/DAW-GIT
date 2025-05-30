from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daw_git_gui import DAWGitApp

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt

from ui_strings import (
    RETURN_TO_LATEST_BTN,
    BTN_COMMIT_NOW,
    BTN_TAG_MAIN_MIX,
    BTN_TAG_CREATIVE_TAKE,
    BTN_TAG_ALT_MIX,
    BTN_TAG_CUSTOM_LABEL,
    BTN_LAUNCH_DAW_FILE,
    COMMIT_REQUIRED_MSG,
    COMMIT_REQUIRED_MSG,
    SNAPSHOT_EDIT_BLOCK_TOOLTIP, 
    TOOLTIP_RETURN_TO_LATEST,
    TOOLTIP_LAUNCH_DAW_FILE,  
    TAG_MAIN_MIX_LABEL,
    TAG_CREATIVE_LABEL,
    TAG_ALT_LABEL
)


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
        self.return_to_latest_btn = QPushButton(RETURN_TO_LATEST_BTN)
        self.return_to_latest_btn.setToolTip(TOOLTIP_RETURN_TO_LATEST)
        if parent and hasattr(parent, "return_to_latest_clicked"):
            self.return_to_latest_btn.clicked.connect(parent.return_to_latest_clicked)
        layout.addWidget(self.return_to_latest_btn)

        # 💾 Commit button
        self.commit_button = QPushButton(BTN_COMMIT_NOW)
        layout.addWidget(self.commit_button)
        self.commit_button.clicked.connect(self.commit_snapshot)

        self.btn_version_main = QPushButton(TAG_MAIN_MIX_LABEL)
        self.btn_version_creative = QPushButton(TAG_CREATIVE_LABEL)
        self.btn_version_alt = QPushButton(TAG_ALT_LABEL)


        # 🏷️ Tagging Buttons
        tag_layout = QHBoxLayout()
        self.tag_main_btn = QPushButton(BTN_TAG_MAIN_MIX)
        self.tag_creative_btn = QPushButton(BTN_TAG_CREATIVE_TAKE)
        self.tag_alt_btn = QPushButton(BTN_TAG_ALT_MIX)
        self.tag_custom_btn = QPushButton(BTN_TAG_CUSTOM_LABEL)
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
        self.open_in_daw_btn = QPushButton(BTN_LAUNCH_DAW_FILE)
        self.open_in_daw_btn.setToolTip(TOOLTIP_LAUNCH_DAW_FILE)
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
            self.snapshot_status_label.setText("") # intentionally blank
            self.snapshot_status_label.setToolTip("") # intentionally blank


    def commit_snapshot(self):
        message = self.commit_message.toPlainText().strip()
        if not message:
            self.status_label.setText(COMMIT_REQUIRED_MSG)
            self.status_label.setText(COMMIT_MESSAGE_REQUIRED_STATUS)
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
        # 💾 Commit button + message
        self.commit_button.setEnabled(enabled)
        self.commit_button.setToolTip(tooltip)

        self.commit_message.setEnabled(enabled)
        self.commit_message.setToolTip(tooltip)

        # 🏷️ Tagging buttons
        self.tag_main_btn.setEnabled(enabled)
        self.tag_main_btn.setToolTip(tooltip)

        self.tag_alt_btn.setEnabled(enabled)
        self.tag_alt_btn.setToolTip(tooltip)

        self.tag_creative_btn.setEnabled(enabled)
        self.tag_creative_btn.setToolTip(tooltip)

        self.tag_custom_btn.setEnabled(enabled)
        self.tag_custom_btn.setToolTip(tooltip)

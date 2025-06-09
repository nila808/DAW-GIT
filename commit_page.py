from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daw_git_gui import DAWGitApp

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QCheckBox, QMessageBox
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
    COMMIT_MESSAGE_REQUIRED_STATUS,
    DETACHED_COMMIT_MSG,
    SNAPSHOT_EDIT_BLOCK_TOOLTIP, 
    SNAPSHOT_PREVIEW_SUMMARY,
    STATUS_READY,
    SNAPSHOT_SAFETY_COMMIT_TITLE,
    SNAPSHOT_SAFETY_COMMIT_MSG,
    SNAPSHOT_BRANCH_MAIN_LABEL,
    SNAPSHOT_BRANCH_OTHER_LABEL,
    SNAPSHOT_SAFETY_BTN_START_NEW,
    SNAPSHOT_SAFETY_BTN_RETURN_LATEST,
    SNAPSHOT_SAFETY_BTN_CANCEL,
    TOOLTIP_RETURN_TO_LATEST,
    TOOLTIP_LAUNCH_DAW_FILE,  
    TAG_MAIN_MIX_LABEL,
    TAG_CREATIVE_LABEL,
    TAG_ALT_LABEL, 
    COMMIT_MESSAGE_REQUIRED_STATUS, 
    TAKE_LOADED_MSG,     
    MODAL_BTN_START_ALT,
    MODAL_BTN_RETURN_LATEST,
    MODAL_BTN_CANCEL, 
    ROLE_MAIN_MIX_TOOLTIP, 
    ROLE_CREATIVE_TOOLTIP, 
    ROLE_ALT_TOOLTIP, 
    ROLE_CUSTOM_TAG_TOOLTIP

)


class CommitPage(QWidget):
    def __init__(self, app=None, parent=None):
        super().__init__(parent)
        self.app = app  # 🔗 Store main app reference


        layout = QVBoxLayout(self)

        # 🎼 Title
        self.title_label = QLabel(TAKE_LOADED_MSG)
        layout.addWidget(self.title_label)

        self.snapshot_status_label = QLabel("")
        self.snapshot_status_label.setObjectName("snapshotStatusLabel")
        self.snapshot_status_label.setText(SNAPSHOT_PREVIEW_SUMMARY)
        self.snapshot_status_label.setToolTip(SNAPSHOT_EDIT_BLOCK_TOOLTIP)

        layout.addWidget(self.snapshot_status_label)

        # 📝 Commit message
        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("Describe what changed in this snapshot")
        self.commit_message.setFixedHeight(80)
        layout.addWidget(self.commit_message)

        # 🧠 Auto-save toggle
        self.auto_save_toggle = QCheckBox("Enable Auto-Save")
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
        self.tag_main_btn.setToolTip(ROLE_MAIN_MIX_TOOLTIP)

        self.tag_creative_btn = QPushButton(BTN_TAG_CREATIVE_TAKE)
        self.tag_creative_btn.setToolTip(ROLE_CREATIVE_TOOLTIP)

        self.tag_alt_btn = QPushButton(BTN_TAG_ALT_MIX)
        self.tag_alt_btn.setToolTip(ROLE_ALT_TOOLTIP)

        self.tag_custom_btn = QPushButton(BTN_TAG_CUSTOM_LABEL)
        self.tag_custom_btn.setToolTip(ROLE_CUSTOM_TAG_TOOLTIP)

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
        self.status_label = QLabel(STATUS_READY)
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
            self.snapshot_status_label.setText(SNAPSHOT_PREVIEW_SUMMARY)
            self.snapshot_status_label.setToolTip(SNAPSHOT_EDIT_BLOCK_TOOLTIP)
        else:
            self.snapshot_status_label.setText("") # intentionally blank
            self.snapshot_status_label.setToolTip("") # intentionally blank


    def commit_snapshot(self):
        # 🎧 Block unsafe commits in detached HEAD state
        if self.app.repo and self.app.repo.head.is_detached:
            # Determine which session this take belongs to
            try:
                branch = self.app.repo.active_branch.name
                if branch == "main":
                    branch_line = SNAPSHOT_BRANCH_MAIN_LABEL
                else:
                    branch_line = SNAPSHOT_BRANCH_OTHER_LABEL.format(branch=branch)
            except Exception:
                branch = "unknown"
                branch_line = SNAPSHOT_BRANCH_OTHER_LABEL.format(branch=branch)

            # Format message with dynamic branch_line
            msg = SNAPSHOT_SAFETY_COMMIT_MSG.format(branch_line=branch_line)

            # 🔳 Custom modal with labeled buttons
            box = QMessageBox(self)
            box.setWindowTitle(SNAPSHOT_SAFETY_COMMIT_TITLE)
            box.setText(msg)

            start_btn = box.addButton(MODAL_BTN_START_ALT, QMessageBox.ButtonRole.YesRole)
            return_btn = box.addButton(MODAL_BTN_RETURN_LATEST, QMessageBox.ButtonRole.NoRole)
            cancel_btn = box.addButton(MODAL_BTN_CANCEL, QMessageBox.ButtonRole.RejectRole)

            box.exec()

            if box.clickedButton() == start_btn:
                self.app.create_new_version_line()
                return
            elif box.clickedButton() == return_btn:
                self.app.return_to_latest_clicked()
                return
            else:
                return  # Cancel pressed

        # ✅ Continue with normal commit logic
        message = self.commit_message.toPlainText().strip()
        if not message:
            self.status_label.setText(COMMIT_REQUIRED_MSG)
            if hasattr(self, "snapshot_status"):
                self.snapshot_status.setText(COMMIT_MESSAGE_REQUIRED_STATUS)
            return

        result = self.app.commit_changes(commit_message=message)
        if result["status"] == "success":
            sha = result["sha"][:7]
            self.status_label.setText(f"✅ Committed: {sha}")
            if hasattr(self, "snapshot_status"):
                self.snapshot_status.setText(f"💾 New take saved: {sha}")
            self.commit_message.clear()
        else:
            error_msg = result.get("message", "Unknown error.")
            self.status_label.setText(f"❌ Couldn’t save take:\n{error_msg}")
            if hasattr(self, "snapshot_status"):
                self.snapshot_status.setText("❌ Snapshot failed — check Git log.")
            self.commit_message.clear()



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

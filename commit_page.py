from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daw_git_gui import DAWGitApp

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt

class CommitPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app: 'DAWGitApp' = parent  # ✅ Clean, type-safe, no circular import

        layout = QVBoxLayout(self)

        # 🎼 Title
        self.title_label = QLabel("📥 Commit Snapshot")
        layout.addWidget(self.title_label)

        # 📝 Commit message
        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("Describe what changed in this snapshot")
        self.commit_message.setFixedHeight(80)
        layout.addWidget(self.commit_message)

        # 🧠 Auto-save toggle
        self.auto_save_toggle = QCheckBox("Enable Auto-Snapshot")
        layout.addWidget(self.auto_save_toggle)
        self.auto_save_toggle.stateChanged.connect(self.toggle_auto_commit)

        # 💾 Commit button
        self.commit_button = QPushButton("💾 Commit Now")
        layout.addWidget(self.commit_button)
        self.commit_button.clicked.connect(self.commit_snapshot)

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

        # 🎯 Status label
        self.status_label = QLabel("📦 Ready to commit")
        layout.addWidget(self.status_label)

        # Link buttons to app for timer updates
        if hasattr(self.app, "commit_button") is False:
            self.app.commit_button = self.commit_button
        if hasattr(self.app, "auto_save_toggle") is False:
            self.app.auto_save_toggle = self.auto_save_toggle



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
            self.status_label.setText(f"❌ Commit failed: {result.get('message')}")

    def toggle_auto_commit(self, state):
        self.app.handle_auto_save_toggle(state)

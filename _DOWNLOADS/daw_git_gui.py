#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import shutil
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QInputDialog,
    QHeaderView
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from git import Repo, InvalidGitRepositoryError, NoSuchPathError

if QApplication.instance() is None:
    _app = QApplication(sys.argv)

class DAWGitApp(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_path = Path.home() / ".dawgit_settings"
        self.repo = None
        self.project_path = self.load_last_project_path() or Path.cwd()
        self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]
        self.current_commit_id = None
        self.setup_ui()
        self.init_git()

    def setup_ui(self):
        self.setWindowTitle("DAW Git Version Control")
        self.setWindowIcon(QIcon(str(self.resource_path("icon.png"))))
        self.resize(800, 900)
        layout = QVBoxLayout()
        self.project_label = QLabel(f"Tracking: {self.project_path}")
        layout.addWidget(self.project_label)

        self.commit_message = QTextEdit()
        self.commit_tag = QTextEdit()
        layout.addWidget(QLabel("Message:"))
        layout.addWidget(self.commit_message)
        layout.addWidget(QLabel("Tag (optional):"))
        layout.addWidget(self.commit_tag)

        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(self.commit_changes)
        layout.addWidget(commit_button)

        self.setLayout(layout)

    def init_git(self):
        try:
            self.repo = Repo(self.project_path)
            if self.repo.head.is_valid():
                self.current_commit_id = self.repo.head.commit.hexsha
            self.update_log()
        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repo = None

    def update_log(self):
        print("[DEBUG] update_log() called")
        if self.repo:
            for commit in self.repo.iter_commits(max_count=5):
                print(f" - {commit.hexsha[:7]}: {commit.message.strip()}")

    def commit_changes(self):
        if not self.repo:
            QMessageBox.warning(self, "No Repo", "Please set up your project first.")
            return

        message = self.commit_message.toPlainText().strip()
        tag = self.commit_tag.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Missing Message", "Please enter a commit message.")
            return

        subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)
        if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
            QMessageBox.information(self, "No Changes", "No changes to commit.")
            return

        commit = self.repo.index.commit(message)
        self.current_commit_id = commit.hexsha
        if tag:
            if tag not in [t.name for t in self.repo.tags]:
                self.repo.create_tag(tag, ref=commit.hexsha)

        self.commit_message.clear()
        self.commit_tag.clear()
        self.update_log()
        QMessageBox.information(self, "Committed", f"Commit complete: {message}")

    def resource_path(self, relative_path):
        if getattr(sys, '_MEIPASS', False):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).parent / relative_path

    def save_last_project_path(self):
        try:
            with open(self.settings_path, "w") as f:
                f.write(str(self.project_path))
        except Exception as e:
            print(f"❌ Failed to save last project path: {e}")

    def load_last_project_path(self):
        try:
            if self.settings_path.exists():
                return Path(self.settings_path.read_text().strip())
        except Exception as e:
            print(f"❌ Failed to load last project path: {e}")
        return None

    def custom_env(self):
        env = os.environ.copy()
        env["PATH"] = self.env_path
        print(f"📌 Using PATH: {env['PATH']}")
        return env

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DAWGitApp()
    win.show()
    sys.exit(app.exec())

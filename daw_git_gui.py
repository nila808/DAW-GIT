#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QInputDialog
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from git import Repo, InvalidGitRepositoryError, NoSuchPathError

# --- Developer Configuration ---
DEVELOPER_MODE = True

class DAWGitApp(QWidget):

    def __init__(self):
        super().__init__()
        self.repo = None
        self.project_path = Path.cwd()
        self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]
        self.current_commit_id = None
        
        self.setup_ui()
        self.init_git()

    def setup_ui(self):
        self.setWindowTitle("DAW Git Version Control")
        self.setWindowIcon(QIcon(str(self.resource_path("icon.png"))))
        self.resize(800, 900)

        main_layout = QVBoxLayout()

        # Project Setup
        setup_btn = QPushButton("SETUP PROJECT")
        setup_btn.clicked.connect(self.run_setup)
        remote_checkbox = QCheckBox("Remote push")
        self.remote_checkbox = remote_checkbox

        setup_layout = QHBoxLayout()
        setup_layout.addWidget(setup_btn)
        setup_layout.addWidget(remote_checkbox)

        main_layout.addLayout(setup_layout)

        # Commit Controls
        commit_group = QGroupBox("Commit Changes")
        commit_layout = QVBoxLayout()

        self.commit_message = QTextEdit(placeholderText="Enter commit message")
        self.commit_tag = QTextEdit(placeholderText="Enter tag (optional)")
        self.commit_tag.setMaximumHeight(40)

        commit_btn = QPushButton("COMMIT CHANGES")
        commit_btn.clicked.connect(self.commit_changes)

        commit_layout.addWidget(QLabel("Commit Message:"))
        commit_layout.addWidget(self.commit_message)
        commit_layout.addWidget(QLabel("Tag:"))
        commit_layout.addWidget(self.commit_tag)
        commit_layout.addWidget(commit_btn)

        commit_group.setLayout(commit_layout)
        main_layout.addWidget(commit_group)

        # Commit History
        history_group = QGroupBox("Commit History")
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Tag", "Commit ID", "Message"])
        self.history_table.cellClicked.connect(self.clear_highlight_on_click)

        checkout_btn = QPushButton("Checkout Selected Version")
        checkout_btn.clicked.connect(self.checkout_commit)
        latest_btn = QPushButton("Return to Latest Version")
        latest_btn.clicked.connect(self.checkout_latest)
        current_btn = QPushButton("What commit am I on?")
        current_btn.clicked.connect(self.highlight_current_commit)

        history_layout.addWidget(self.history_table)
        history_layout.addWidget(checkout_btn)
        history_layout.addWidget(latest_btn)
        history_layout.addWidget(current_btn)

        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)

        self.setLayout(main_layout)

    def resource_path(self, relative_path):
        if getattr(sys, '_MEIPASS', False):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).parent / relative_path

    def init_git(self):
        try:
            self.repo = Repo(self.project_path)
            print(f"✅ Git repository found at {self.project_path}")
            self.update_log()
        except (InvalidGitRepositoryError, NoSuchPathError):
            print(f"❌ No Git repository at {self.project_path}")

    def run_setup(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            try:
                self.project_path = Path(folder)
                os.chdir(self.project_path)

                if (self.project_path / ".git").exists():
                    print("ℹ️ Existing Git repo found — skipping init.")
                    self.init_git()
                    return

                print(f"🚀 Initializing Git at: {self.project_path}")

                subprocess.run(["git", "init"], env=self.custom_env(), check=True)
                subprocess.run(["git", "lfs", "install"], env=self.custom_env(), check=True)

                (self.project_path / ".gitignore").write_text("*.als~\n*.logicx~\n*.asd\n*.tmp\n.DS_Store\n", encoding='utf-8')
                (self.project_path / ".gitattributes").write_text("*.als filter=lfs diff=lfs merge=lfs -text\n", encoding='utf-8')

                subprocess.run(["git", "add", "."], env=self.custom_env(), check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], env=self.custom_env(), check=True)
                subprocess.run(["git", "branch", "-M", "main"], env=self.custom_env(), check=True)

                QMessageBox.information(self, "Setup Complete", "✅ Git repository initialized.")
                print("🎉 Git setup completed and initial commit made successfully.")
                self.init_git()

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Git Setup Failed", f"Subprocess error: {e}")
                print(f"❌ Subprocess failed: {e}")

            except Exception as e:
                QMessageBox.critical(self, "Setup Failed", f"Unexpected error: {e}")
                print(f"❌ Unexpected error during setup: {e}")

    def commit_changes(self):
        if not self.repo:
            QMessageBox.warning(self, "No Repo", "Initialize the repository first.")
            return

        msg = self.commit_message.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Commit Failed", "Commit message required.")
            return

        try:
            subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)

            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(self, "No Changes", "There are no new changes to commit.")
                print("ℹ️ No changes to commit.")
                return

            commit = self.repo.index.commit(msg)

            tag = self.commit_tag.toPlainText().strip()
            if tag:
                self.repo.create_tag(tag, ref=commit.hexsha)

            if self.remote_checkbox.isChecked():
                subprocess.run(["git", "push", "origin", "main", "--tags"], cwd=self.project_path, env=self.custom_env(), check=True)

            self.update_log()
            self.commit_message.clear()
            self.commit_tag.clear()

            QMessageBox.information(self, "Committed", "✅ Changes committed successfully.")
            print(f"✅ Commit '{msg}' completed.")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Commit Failed", f"Subprocess error: {e}")
            print(f"❌ Subprocess error during commit: {e}")

        except Exception as e:
            QMessageBox.critical(self, "Commit Failed", f"Unexpected error: {e}")
            print(f"❌ Unexpected error during commit: {e}")

    def update_log(self):
        self.history_table.setRowCount(0)
        for i, commit in enumerate(self.repo.iter_commits(max_count=50)):
            self.history_table.insertRow(i)
            tag = next((t.name for t in self.repo.tags if t.commit == commit), '')
            self.history_table.setItem(i, 0, QTableWidgetItem(tag))
            self.history_table.setItem(i, 1, QTableWidgetItem(commit.hexsha[:7]))
            self.history_table.setItem(i, 2, QTableWidgetItem(commit.message.strip()))

        # Reselect previously checked out commit if applicable
        if self.current_commit_id:
            for i in range(self.history_table.rowCount()):
                if self.history_table.item(i, 1).text() == self.current_commit_id[:7]:
                    self.history_table.selectRow(i)
                    break

    def checkout_commit(self):
        row = self.history_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Select a commit first.")
            return
        commit_id = self.history_table.item(row, 1).text()
        self.repo.git.checkout(commit_id)
        self.current_commit_id = commit_id
        print(f"🔄 Checked out commit {commit_id}")

        # ✅ User feedback and highlight the row
        self.update_log()
        self.status_message(f"Checked out commit: {commit_id}")
        self.history_table.selectRow(row)
        QMessageBox.information(self, "Checkout Complete", f"✅ Now viewing commit {commit_id}")

    def highlight_current_commit(self):
        try:
            current_commit = self.repo.head.commit.hexsha[:7]
            self.current_commit_id = current_commit
            self.update_log()
            QMessageBox.information(self, "Current Commit", f"✅ You are on commit: {current_commit}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not determine current commit: {e}")

    def clear_highlight_on_click(self):
        self.current_commit_id = None

    def checkout_latest(self):
        self.repo.git.checkout("main")
        # Get latest commit ID after checking out main
        latest_commit = next(self.repo.iter_commits('main', max_count=1))
        self.current_commit_id = latest_commit.hexsha
        print("🔄 Returned to main branch.")
        self.update_log()
        self.status_message("Returned to latest version (main branch)")

    def status_message(self, message):
        print(f"[STATUS] {message}")

    def custom_env(self):
        env = os.environ.copy()
        env["PATH"] = self.env_path
        print(f"📌 Using PATH: {env['PATH']}")
        return env

# Proper App Exit
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DAWGitApp()
    win.show()
    sys.exit(app.exec())

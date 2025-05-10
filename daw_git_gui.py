#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import shutil
import traceback
from datetime import datetime
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
    def __init__(self, build_ui=True):
        super().__init__()

        self.settings_path = Path.home() / ".dawgit_settings"
        self.repo = None
        self.project_path = self.load_last_project_path() or Path.cwd()
        self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]
        self.current_commit_id = None

        if build_ui:
            self.setup_ui()
        self.init_git()

    def setup_ui(self):
        self.setWindowTitle("DAW Git Version Control")
        self.setWindowIcon(QIcon(str(self.resource_path("icon.png"))))
        self.resize(800, 900)
        main_layout = QVBoxLayout()

        # 🔁 Uncommitted changes indicator
        self.unsaved_indicator = QLabel("● Uncommitted Changes")
        self.unsaved_indicator.setStyleSheet("color: orange; font-weight: bold;")
        self.unsaved_indicator.setVisible(False)
        self.unsaved_flash = False
        self.unsaved_timer = self.startTimer(800)
        main_layout.addWidget(self.unsaved_indicator)

        # 📁 Project tracking label
        self.project_label = QLabel()
        self.project_label.setText(f"Tracking: {self.project_path}")
        self.project_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.project_label.setOpenExternalLinks(True)
        self.project_label.setToolTip("Click to open in Finder")
        self.project_label.setWordWrap(True)
        main_layout.addWidget(self.project_label)

        # Project Setup button
        setup_btn = QPushButton("Setup Project")
        setup_btn.clicked.connect(self.run_setup)
        main_layout.addWidget(setup_btn)

        # 🧰 Control buttons row
        controls_layout = QHBoxLayout()

        change_btn = QPushButton("Change Project Folder")
        change_btn.clicked.connect(self.change_project_folder)

        clear_btn = QPushButton("Clear Saved Project")
        clear_btn.clicked.connect(self.clear_saved_project)

        snapshot_export_btn = QPushButton("Export Snapshot")
        snapshot_export_btn.clicked.connect(self.export_snapshot)

        snapshot_import_btn = QPushButton("Import Snapshot")
        snapshot_import_btn.clicked.connect(self.import_snapshot)

        restore_btn = QPushButton("Restore Last Backup")
        restore_btn.clicked.connect(self.restore_last_backup)

        controls_layout.addWidget(change_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(snapshot_export_btn)
        controls_layout.addWidget(snapshot_import_btn)
        controls_layout.addWidget(restore_btn)

        main_layout.addLayout(controls_layout)

        # 📝 Commit inputs
        self.commit_message = QTextEdit(placeholderText="Enter commit message")
        self.commit_tag = QTextEdit(placeholderText="Enter tag (optional)")
        self.commit_tag.setMaximumHeight(40)

        commit_btn = QPushButton("COMMIT CHANGES")
        commit_btn.clicked.connect(self.commit_changes)

        auto_commit_btn = QPushButton("AUTO COMMIT")
        auto_commit_btn.clicked.connect(lambda: self.auto_commit("Auto snapshot", "auto"))


        commit_layout = QVBoxLayout()
        commit_layout.addWidget(QLabel("Commit Message:"))
        commit_layout.addWidget(self.commit_message)
        commit_layout.addWidget(QLabel("Tag:"))
        commit_layout.addWidget(self.commit_tag)
        commit_layout.addWidget(commit_btn)
        commit_layout.addWidget(auto_commit_btn)

        main_layout.addLayout(commit_layout)

        checkout_layout = QHBoxLayout()
        checkout_latest_btn = QPushButton("Checkout Latest Commit")
        checkout_latest_btn.clicked.connect(self.checkout_latest)

        checkout_selected_btn = QPushButton("Checkout Selected Commit")
        checkout_selected_btn.clicked.connect(self.checkout_selected_commit)

        # 🔍 "What commit am I on?" button
        show_commit_btn = QPushButton("Show Current Commit")
        show_commit_btn.clicked.connect(self.highlight_current_commit)

        # Checkout buttons
        checkout_layout.addWidget(checkout_latest_btn)
        checkout_layout.addWidget(checkout_selected_btn)
        checkout_layout.addWidget(show_commit_btn)
        main_layout.addLayout(checkout_layout)

        # ✅ Remote push option
        self.remote_checkbox = QCheckBox("Push to remote after commit")
        main_layout.addWidget(self.remote_checkbox)

        # 🧾 History table
        history_group = QGroupBox("Commit History")
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget(0, 3)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setHorizontalHeaderLabels(["Tag", "Commit ID", "Message"])
        self.history_table.resizeColumnsToContents()
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)

        self.setLayout(main_layout)


    def init_git(self):
        self.save_last_project_path()
        if hasattr(self, 'project_label'):
            self.project_label.setText(f"Tracking: {self.project_path}")
        try:
            self.repo = Repo(self.project_path)
            print(f"✅ Git repository found at {self.project_path}")

            if self.repo.head.is_valid():
                self.current_commit_id = self.repo.head.commit.hexsha
            else:
                self.current_commit_id = None
                print("⚠️ Repo exists but has no commits yet.")

            self.update_unsaved_indicator()
            self.update_log()
        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repo = None
            print(f"❌ No Git repository at {self.project_path}")

    def update_log(self):
        if not hasattr(self, "history_table"):
            print("⚠️ Skipping update_log(): no history_table defined yet.")
            return

        if not self.repo or not self.repo.head.is_valid():
            print("ℹ️ Skipping update_log — no commits found.")
            return

        for i, commit in enumerate(self.repo.iter_commits(max_count=50)):
            self.history_table.insertRow(i)
            tag = next((t.name for t in self.repo.tags if t.commit == commit), '')
            tag_item = QTableWidgetItem(tag)
            commit_id_item = QTableWidgetItem(f"[{i}] {commit.hexsha[:7]} ({commit.committed_datetime.strftime('%Y-%m-%d')} by {commit.author.name})")
            message_item = QTableWidgetItem(commit.message.strip())
            self.history_table.setItem(i, 0, tag_item)
            self.history_table.setItem(i, 1, commit_id_item)
            self.history_table.setItem(i, 2, message_item)

            tag_item.setToolTip(tag)
            commit_id_item.setToolTip(commit.hexsha)
            message_item.setToolTip(commit.message.strip())

            self.history_table.resizeColumnsToContents()

            if self.current_commit_id and commit.hexsha.startswith(self.current_commit_id[:7]):
                for col in range(self.history_table.columnCount()):
                    item = self.history_table.item(i, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.green)

        if self.current_commit_id:
            for i in range(self.history_table.rowCount()):
                if self.history_table.item(i, 1) and self.current_commit_id[:7] in self.history_table.item(i, 1).text():
                    self.history_table.selectRow(i)
                    break

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
                subprocess.run(["git", "init"], cwd=self.project_path, env=self.custom_env(), check=True)
                subprocess.run(["git", "lfs", "install"], cwd=self.project_path, env=self.custom_env(), check=True)

                (self.project_path / ".gitignore").write_text("*.als~\n*.logicx~\n*.asd\n*.tmp\n.DS_Store\n", encoding='utf-8')
                (self.project_path / ".gitattributes").write_text("*.als filter=lfs diff=lfs merge=lfs -text\n", encoding='utf-8')

                subprocess.run(["git", "add", "."], cwd=self.project_path, env=self.custom_env(), check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.project_path, env=self.custom_env(), check=True)
                subprocess.run(["git", "branch", "-M", "main"], cwd=self.project_path, env=self.custom_env(), check=True)

                QMessageBox.information(self, "Setup Complete", "✅ Git repository initialized.")
                self.init_git()

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Git Setup Failed", f"Subprocess error: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Setup Failed", f"Unexpected error: {e}")

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
                return

            commit = self.repo.index.commit(msg)

            tag = self.commit_tag.toPlainText().strip()
            if tag:
                if tag in [t.name for t in self.repo.tags]:
                    print(f"⚠️ Tag '{tag}' already exists. Skipping tag creation.")
                else:
                    self.repo.create_tag(tag, ref=commit.hexsha)

            if self.remote_checkbox.isChecked():
                subprocess.run(["git", "push", "origin", "main", "--tags"], cwd=self.project_path, env=self.custom_env(), check=True)

            self.update_log()
            self.update_unsaved_indicator()
            self.commit_message.clear()
            self.commit_tag.clear()

            QMessageBox.information(self, "Committed", "✅ Changes committed successfully.")
            print(f"✅ Commit '{msg}' completed.")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Commit Failed", f"Subprocess error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Commit Failed", f"Unexpected error: {e}")

    def auto_commit(self, message: str, tag: str = ""):
        if not self.repo:
            QMessageBox.warning(self, "No Repo", "Initialize the repository first.")
            return

        try:
            subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)

            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(self, "No Changes", "There are no new changes to commit.")
                return

            commit = self.repo.index.commit(message)

            if tag:
                subprocess.run(["git", "tag", tag, commit.hexsha], cwd=self.project_path, env=self.custom_env(), check=True)

            self.update_log()
            QMessageBox.information(self, "Auto Commit", f"✅ Auto-commit successful:\n{message}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Auto Commit Failed", f"Subprocess error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Auto Commit Failed", f"Unexpected error: {e}")

    def checkout_selected_commit(self):
        try:
            selected_row = self.history_table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "No Selection", "Please select a commit to check out.")
                return
            commit_id = self.history_table.item(selected_row, 1).toolTip()
            subprocess.run(["git", "checkout", commit_id], cwd=self.project_path, env=self.custom_env(), check=True)
            self.init_git()
            QMessageBox.information(self, "Checked Out", f"✅ Now on commit {commit_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to checkout selected commit: {e}")

   
    def has_unsaved_changes(self):
        return self.repo and self.repo.is_dirty(index=True, working_tree=True, untracked_files=True)

    def backup_unsaved_changes(self):
        backup_dir = self.project_path.parent / f"Backup_{self.project_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        for file in self.project_path.glob("*.*"):
            if file.is_file():
                shutil.copy(file, backup_dir / file.name)
        print(f"🔒 Unsaved changes backed up to: {backup_dir}")

    def export_snapshot(self):
        import traceback
        try:
            if not self.project_path or not self.project_path.exists():
                QMessageBox.warning(self, "No Project", "No project folder selected.")
                return

            target_dir = QFileDialog.getExistingDirectory(self, "Select Folder to Save Snapshot")
            if not target_dir:
                return

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            snapshot_name = f"{self.project_path.name}_snapshot_{timestamp}"
            dest = os.path.join(target_dir, snapshot_name)

            # Avoid exporting .git folder
            for item in os.listdir(self.project_path):
                if item == ".git":
                    continue
                src = os.path.join(self.project_path, item)
                dst = os.path.join(dest, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)

            QMessageBox.information(self, "Export Complete", f"Snapshot saved to:\n{dest}")

        except Exception as e:
            print("❌ Error during snapshot export:")
            traceback.print_exc()
            QMessageBox.critical(self, "Export Failed", f"Error: {e}")


    def import_snapshot(self):
        import traceback
        try:
            src_folder = QFileDialog.getExistingDirectory(self, "Select Snapshot Folder to Import")
            if not src_folder:
                return

            target_path = self.project_path
            if not target_path or not target_path.exists():
                QMessageBox.warning(self, "Invalid Project", "Target project folder is not set.")
                return

            for item in os.listdir(src_folder):
                if item == ".git":
                    continue  # 🚫 Never import .git folder

                s = os.path.join(src_folder, item)
                d = os.path.join(target_path, item)

                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            QMessageBox.information(self, "Import Complete", f"Snapshot imported into:\n{target_path}")
            self.init_git()

        except Exception as e:
            print("❌ Error during snapshot import:")
            traceback.print_exc()
            QMessageBox.critical(self, "Import Failed", f"Error: {e}")

    def checkout_commit(self):
        row = self.history_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a commit first.")
            return

        commit_id_item = self.history_table.item(row, 1)
        if not commit_id_item:
            QMessageBox.critical(self, "Error", "Commit ID not found in selected row.")
            return

        try:
            commit_id = commit_id_item.text().split()[1]
        except IndexError:
            QMessageBox.critical(self, "Error", "Malformed commit ID text.")
            return

        if self.has_unsaved_changes():
            if QMessageBox.question(
                self, "Unsaved Changes Detected",
                "You have unsaved changes. Backup before switching?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
                self.backup_unsaved_changes()

            try:
                subprocess.run(["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"], cwd=self.project_path, env=self.custom_env(), check=True)
                print("📦 Stashed unsaved changes before checkout.")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Stash Failed", f"Unable to stash changes: {e}")
                return

        try:
            self.repo.git.checkout(commit_id)
            self.current_commit_id = commit_id
            print(f"🔄 Checked out commit {commit_id}")
            self.update_log()
            self.status_message(f"Checked out commit: {commit_id}")
            self.history_table.selectRow(row)
            QMessageBox.information(self, "Checkout Complete", f"✅ Now viewing commit {commit_id}")
        except Exception as e:
            QMessageBox.critical(self, "Checkout Failed", str(e))

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
        if self.has_unsaved_changes():
            if QMessageBox.question(self, "Unsaved Changes Detected", "You have unsaved changes. Backup before switching?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.backup_unsaved_changes()

        self.repo.git.checkout("main")
        latest_commit = next(self.repo.iter_commits('main', max_count=1))
        self.current_commit_id = latest_commit.hexsha
        print("🔄 Returned to main branch.")
        self.update_log()
        self.status_message("Returned to latest version (main branch)")

    def open_project_folder(self, event):
        if self.project_path.exists():
            subprocess.run(["open", str(self.project_path)])

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

    def clear_saved_project(self):
        if self.settings_path.exists():
            try:
                self.settings_path.unlink()
                QMessageBox.information(self, "Cleared", "✅ Saved project path has been cleared. It will default to current directory on next launch.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Failed to clear project path: {e}")
        else:
            QMessageBox.information(self, "No Saved Path", "ℹ️ No saved project path found to clear.")

    def auto_commit(self, message: str, tag: str = ""):
        if not self.repo:
            QMessageBox.warning(self, "No Repo", "Initialize the repository first.")
            return

        try:
            subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)

            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(self, "No Changes", "There are no new changes to commit.")
                return

            commit = self.repo.index.commit(message)

            if tag:
                if tag in [t.name for t in self.repo.tags]:
                    print(f"⚠️ Tag '{tag}' already exists. Skipping tag creation.")
                else:
                    self.repo.create_tag(tag, ref=commit.hexsha)

            if self.remote_checkbox.isChecked():
                subprocess.run(["git", "push", "origin", "main", "--tags"], cwd=self.project_path, env=self.custom_env(), check=True)

            self.update_log()
            msg = f"✅ Auto-commit successful:\n{message}"

            QMessageBox.information(self, "Auto Commit", msg)
            print(f"✅ Auto-committed: {message}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Auto Commit Failed", f"Subprocess error: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Auto Commit Failed", f"Unexpected error: {e}")

    def change_project_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select New Project Folder")
        if folder:
            self.project_path = Path(folder)
            os.chdir(self.project_path)
            self.init_git()

    def status_message(self, message):
        print(f"[STATUS] {message}")

    def custom_env(self):
        env = os.environ.copy()
        env["PATH"] = self.env_path
        print(f"📌 Using PATH: {env['PATH']}")
        return env

    def restore_last_backup(self):
        backups = sorted(Path(self.project_path.parent).glob(f"Backup_{self.project_path.name}_*"), reverse=True)
        if not backups:
            QMessageBox.warning(self, "No Backup Found", "There are no backup folders for this project.")
            return

        latest_backup = backups[0]
        for file in latest_backup.glob("*.*"):
            if file.is_file():
                shutil.copy(file, self.project_path / file.name)

        QMessageBox.information(self, "Backup Restored", f"✅ Restored files from: {latest_backup}")

    def timerEvent(self, event):
        if self.repo and self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
            self.unsaved_flash = not self.unsaved_flash
            color = "orange" if self.unsaved_flash else "transparent"
            self.unsaved_indicator.setStyleSheet(f"color: {color}; font-weight: bold;")
            self.unsaved_indicator.setVisible(True)
        else:
            self.unsaved_indicator.setStyleSheet("color: transparent; font-weight: bold;")
            self.unsaved_flash = False
            self.unsaved_indicator.setVisible(False)


    def update_unsaved_indicator(self):
        if self.repo:
            self.unsaved_indicator.setVisible(self.repo.is_dirty(index=True, working_tree=True, untracked_files=True))

    def resource_path(self, relative_path):
        if getattr(sys, '_MEIPASS', False):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).parent / relative_path

# Handle Ctrl+C gracefully
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DAWGitApp()
    win.show()
    sys.exit(app.exec())

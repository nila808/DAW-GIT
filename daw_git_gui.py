#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import shutil
import traceback
from datetime import datetime
from git.exc import GitCommandError
from pathlib import Path

# Qt Widgets and core modules
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QInputDialog,
    QHeaderView, QScrollArea, QSplitter, QSizePolicy, QStyle, QMenu
)
from PyQt6.QtGui import QIcon, QPixmap, QAction  # ✅ Correct location for QAction
from PyQt6.QtCore import Qt

# Optional: for namespace-style usage (if you're using QtCore/QtGui/QtWidgets in older code)
from PyQt6 import QtCore, QtGui, QtWidgets

# Ensure QApplication exists
if QApplication.instance() is None:
    _app = QApplication(sys.argv)

# Git modules
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

        self.status_label = QLabel("Status: Ready")
        self.status_label.setObjectName("status_label")
        main_layout.addWidget(self.status_label)


        main_layout.addWidget(self.project_label)

        # ✅ Add path_label for tests - UNCOMMENT WHEN RUNNING TESTS
        self.path_label = QLabel(str(self.project_path))
        main_layout.addWidget(self.path_label)
        
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

        # ⬅️ Checkout + Info buttons
        checkout_layout = QHBoxLayout()
        checkout_latest_btn = QPushButton("Return to Latest Commit")
        checkout_latest_btn.clicked.connect(self.checkout_latest)

        checkout_selected_btn = QPushButton("Checkout Selected Commit")
        checkout_selected_btn.clicked.connect(self.checkout_selected_commit)

        what_commit_btn = QPushButton("What Commit Am I In?")
        what_commit_btn.clicked.connect(self.show_current_commit)

        branch_switch_btn = QPushButton("🔀 Switch to Saved Version")
        branch_switch_btn.clicked.connect(self.switch_branch)

        checkout_layout.addWidget(checkout_latest_btn)
        checkout_layout.addWidget(checkout_selected_btn)
        checkout_layout.addWidget(what_commit_btn)
        checkout_layout.addWidget(branch_switch_btn)
        main_layout.addLayout(checkout_layout)

        # 🎼 Start New Version Line
        self.new_version_line_button = QPushButton("🎼 Start New Version Line")
        self.new_version_line_button.clicked.connect(self.start_new_version_line)
        main_layout.addWidget(self.new_version_line_button)

        # 🎚️ Current branch indicator
        self.version_line_label = QLabel()
        self.version_line_label.setText("🎚️ No active version line")
        self.version_line_label.setStyleSheet("color: #999; font-style: italic;")
        main_layout.addWidget(self.version_line_label)


        # ✅ Remote push option
        self.remote_checkbox = QCheckBox("Push to remote after commit")
        main_layout.addWidget(self.remote_checkbox)

        # History table
        history_group = QGroupBox("Commit History")
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget(0, 3)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # 🎧 Launch Ableton button (hidden by default)
        self.open_als_button = QPushButton("🎧 Open This Version in Ableton")
        self.open_als_button.setVisible(False)
        self.open_als_button.clicked.connect(self.open_latest_daw_project)

        main_layout.addWidget(self.open_als_button)

        # Set stretch + autosize behavior
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_commit_context_menu)

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
                print(f"[DEBUG] Current commit ID: {self.current_commit_id[:7]}")
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

        self.history_table.setRowCount(0)  # Clear previous rows
        self.history_table.clearSelection()  # ✅ Also clear previous selection

        if not self.repo or not self.repo.head.is_valid():
            print("ℹ️ Skipping update_log — no commits found.")
            return

        commits = list(self.repo.iter_commits(max_count=50))
        commits.reverse()  # ✅ Align row order with modals


        for i, commit in enumerate(commits):
            self.history_table.insertRow(i)
            tag = next((t.name for t in self.repo.tags if t.commit == commit), '')
            tag_item = QTableWidgetItem(tag)
            commit_id_item = QTableWidgetItem(
                f"[#{i+1}] [{commit.hexsha[:7]}] ({commit.committed_datetime.strftime('%Y-%m-%d')} by {commit.author.name})"
            )
            message_item = QTableWidgetItem(commit.message.strip())

            self.history_table.setItem(i, 0, tag_item)
            self.history_table.setItem(i, 1, commit_id_item)
            self.history_table.setItem(i, 2, message_item)

            tag_item.setToolTip(tag)
            commit_id_item.setToolTip(commit.hexsha)
            message_item.setToolTip(commit.message.strip())

            if self.current_commit_id == commit.hexsha:
                for col in range(self.history_table.columnCount()):
                    item = self.history_table.item(i, col)
                    if item:
                        item.setBackground(Qt.GlobalColor.green)
                self.history_table.selectRow(i)
            print(f"[DEBUG] Comparing {self.current_commit_id[:7]} to {commit.hexsha[:7]} (row {i})")

            # ✅ Disable Delete button if selected commit is unreachable
            if hasattr(self, "delete_commit_button") and self.repo:
                try:
                    reachable = [c.hexsha for c in self.repo.iter_commits()]
                    if self.current_commit_id in reachable:
                        self.delete_commit_button.setEnabled(True)
                        self.delete_commit_button.setToolTip("Delete this commit from history.")
                    else:
                        self.delete_commit_button.setEnabled(False)
                        self.delete_commit_button.setToolTip("❌ This commit is from another version line and cannot be deleted from here.")
                except Exception as e:
                    print(f"[WARN] Could not validate commit reachability: {e}")

        self.history_table.resizeColumnsToContents()

        # ✅ Auto-scroll to selected row
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            self.history_table.scrollToItem(self.history_table.item(selected_row, 0), QTableWidget.ScrollHint.PositionAtCenter)

        # ✅ Enable or disable the delete commit button
        if hasattr(self, "delete_commit_button") and self.current_commit_id:
            can_delete = self.is_commit_deletable(self.current_commit_id)
            self.delete_commit_button.setEnabled(can_delete)
            self.delete_commit_button.setToolTip(
                "Delete this commit from history." if can_delete else
                "This commit is protected or not part of the current branch."
            )
            print(f"[DEBUG] Final selected row after update_log(): {selected_row}")


    def run_setup(self):
        if not self.project_path or not self.project_path.exists():
            folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not folder:
                return
            self.project_path = Path(folder)

        try:
            os.chdir(self.project_path)

            if (self.project_path / ".git").exists():
                print("ℹ️ Existing Git repo found — skipping init.")
                self.init_git()
                return

            self.open_als_button.setVisible(False)
            print(f"🚀 Initializing Git at: {self.project_path}")

            subprocess.run(["git", "init"], cwd=self.project_path, env=self.custom_env(), check=True)

            # ✅ Auto-ignore backup and temp files
            ignore_entries = [
                "*.als~", "*.logicx~", "*.asd", "*.tmp", ".DS_Store", "Backup/"
            ]
            gitignore_path = self.project_path / ".gitignore"
            existing = gitignore_path.read_text().splitlines() if gitignore_path.exists() else []

            added_entries = []
            with open(gitignore_path, "a", encoding="utf-8") as f:
                for entry in ignore_entries:
                    if entry not in existing:
                        f.write(entry + "\n")
                        added_entries.append(entry)

            if added_entries:
                QMessageBox.information(
                    self,
                    "Ignore Rules Updated",
                    "📂 Backup folder and temporary files are now safely excluded from version control.\n\n"
                    "You’ll only see changes that matter to your music project."
                )
                print("[DEBUG] Added to .gitignore:", added_entries)
            else:
                print("[DEBUG] .gitignore already up to date. No entries added.")

            subprocess.run(["git", "lfs", "install"], cwd=self.project_path, env=self.custom_env(), check=True)

            # ✅ Only write LFS config if .gitattributes doesn’t exist
            gitattributes_path = self.project_path / ".gitattributes"
            if not gitattributes_path.exists():
                gitattributes_path.write_text("*.als filter=lfs diff=lfs merge=lfs -text\n", encoding="utf-8")

            subprocess.run(["git", "add", "."], cwd=self.project_path, env=self.custom_env(), check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.project_path, env=self.custom_env(), check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=self.project_path, env=self.custom_env(), check=True)

            QMessageBox.information(
                self,
                "Setup Complete",
                "🎶 Your project is now tracked with version control!\n\n"
                "You’re ready to loop, branch, and explore your musical ideas safely."
            )
            self.init_git()
            self.open_als_button.setVisible(False)

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Git Setup Failed",
                f"❌ We hit a glitch while setting up Git:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Setup Error",
                f"⚠️ Something went wrong while preparing your session:\n\n{e}"
            )

    def get_default_branch(self):
        try:
            return self.repo.head.reference.name
        except Exception:
            # Fallback in case we're detached
            return self.repo.heads[0].name if self.repo.heads else "main"

    def safe_switch_branch(self, target_branch):
        if self.repo.is_dirty(untracked_files=True):
            return {"status": "warning", "message": "Uncommitted changes present"}
        
        try:
            subprocess.run(
                ["git", "checkout", target_branch],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )
            self.repo = Repo(self.project_path)
            self.init_git()
            self.update_log()
            return {"status": "ok"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}

    def refresh_commit_table(self):
        """Stub method to satisfy tests — actual logic may be implemented later."""
        pass


    def commit_changes(self):
        if not self.repo:
            self.show_status_message("⚠️ No Git repository found.")
            return False

        has_als = any(f.suffix == ".als" for f in self.project_path.glob("*.als"))
        has_logicx = any(f.suffix == ".logicx" for f in self.project_path.glob("*.logicx"))

        if not has_als and not has_logicx:
            self.status_label.setText("⚠️ No .als or .logicx file found to commit.")  # ✅ Needed for test
            return False

        msg = self.commit_message.toPlainText().strip()
        if not msg:
            QMessageBox.warning(
                self,
                "Missing Message",
                "📝 Please enter a short note describing what’s changed in this version."
            )
            return False

        # 🎧 Snapshot safety
        if self.repo.head.is_detached:
            current_branch = "(Snapshot View – no version line active)"
            box = QMessageBox(self)
            box.setWindowTitle("🎧 Snapshot View")
            box.setText(
                f"You’re currently exploring a snapshot of your project.\n\n"
                f"{current_branch}\n\n"
                "Would you like to:\n"
                "🎼 Start a new version line from here?\n"
                "🔁 Return to your main version?\n"
                "❌ Or cancel and stay in snapshot view?"
            )
            box.setIcon(QMessageBox.Icon.Warning)

            save_new_btn = box.addButton("🎼 Save as New Version", QMessageBox.ButtonRole.YesRole)
            return_main_btn = box.addButton("🔁 Return to Main Version", QMessageBox.ButtonRole.NoRole)
            cancel_btn = box.addButton("❌ Cancel", QMessageBox.ButtonRole.RejectRole)

            box.exec()

            if box.clickedButton() == cancel_btn:
                return False
            elif box.clickedButton() == return_main_btn:
                try:
                    subprocess.run(
                        ["git", "checkout", self.get_default_branch()],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        check=True
                    )
                    self.repo = Repo(self.project_path)
                    self.current_commit_id = self.repo.head.commit.hexsha
                    self.init_git()
                    self.update_log()
                    self.project_label.setText(f"Tracking: {self.project_path}")
                    return False
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(
                        self,
                        "Couldn’t Return to Main",
                        f"⚠️ We couldn’t switch back to the main version:\n\n{e}"
                    )
                    return False

            elif box.clickedButton() == save_new_btn:
                new_branch_name, ok = QInputDialog.getText(
                    self,
                    "New Version Line",
                    "🎼 Name your new version line (e.g. 'alt_take', 'bass_fix', or 'idea_bounce'):"
                )
                if ok and new_branch_name:
                    result = self.create_new_version_line(new_branch_name)
                    if result["status"] == "error":
                        QMessageBox.critical(self, "Error", result["message"])
                        return False
                else:
                    return False

        try:
            subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)

            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(
                    self,
                    "No Changes",
                    "✅ No changes to commit — your project is already up to date!"
                )
                return False

            commit = self.repo.index.commit(msg)
            self.current_commit_id = commit.hexsha

            tag = self.commit_tag.toPlainText().strip()
            if tag:
                if tag in [t.name for t in self.repo.tags]:
                    print(f"⚠️ Tag '{tag}' already exists. Skipping tag.")
                else:
                    self.repo.create_tag(tag, ref=commit.hexsha)

            if self.remote_checkbox.isChecked():
                subprocess.run(["git", "push", "origin", self.get_default_branch(), "--tags"],
                            cwd=self.project_path, env=self.custom_env(), check=True)

            self.update_log()
            self.update_unsaved_indicator()
            self.commit_message.clear()
            self.commit_tag.clear()

            QMessageBox.information(
                self,
                "Committed",
                f"✅ Your changes have been saved as a new version:\n\n{msg}"
            )
            print(f"✅ Commit '{msg}' completed.")
            return True

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Commit Failed", f"❌ Git command failed:\n{e}")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Commit Failed", f"⚠️ Something unexpected went wrong:\n{e}")
            return False


    def show_current_commit(self):
        if not self.repo or not self.repo.head.is_valid():
            QMessageBox.information(self, "Commit Info", "No commits yet.")
            return

        commits = list(self.repo.iter_commits(max_count=50))
        commits.reverse()  # ✅ To match UI row order

        current = self.repo.head.commit

        # Index in recent history
        index = next((i for i, c in enumerate(commits) if c.hexsha == current.hexsha), None)
        age_str = "(latest)" if index == 0 else f"({index} commits ago)" if index is not None else "(older)"

        # Message and tag
        short_msg = current.message.strip().split("\n")[0][:40]
        short_hash = current.hexsha[:7]
        tag = next((t.name for t in self.repo.tags if t.commit == current), None)
        # label = f"[#{index + 1 if index is not None else '?'} {short_hash}] - {short_msg} {age_str}"
        label = f"[#{index + 1 if index is not None else '?'} - {short_hash}] - {short_msg} {age_str}"


        timestamp = current.committed_datetime.strftime("%d %b %Y, %H:%M")

        body = f"{label}\n\n" + ("-" * 40) + f"\n\nCommitted: {timestamp}"
        QMessageBox.information(self, "Current Commit", body)


    def create_new_version_line(self, branch_name):
        try:
            # Prevent duplicate branch creation
            if branch_name in [b.name for b in self.repo.branches]:
                self._show_warning(f"Branch '{branch_name}' already exists.")
                return {"status": "error", "message": f"Branch '{branch_name}' already exists."}

            # ✅ Create and switch to new branch (from current commit)
            self.repo.git.checkout("-B", branch_name)

            # ✅ Refresh repo to ensure HEAD is now attached to the new branch
            self.repo = Repo(self.project_path)

            # ✅ Add marker file and commit it
            marker_path = Path(self.project_path) / ".version_marker"
            marker_path.write_text(f"Version line started: {branch_name}")
            self.repo.index.add([str(marker_path.relative_to(self.project_path))])
            commit = self.repo.index.commit(f"🎼 Start New Version Line '{branch_name}'")

            self.refresh_commit_table()
            self._show_info(f"🎼 New version line '{branch_name}' created.")
            return {"status": "success", "commit_message": commit.message.strip()}

        except Exception as e:
            self._show_error(f"Failed to create version line: {e}")
            return {"status": "error", "message": str(e)}
        
        print("🔖 New commit message:", self.repo.head.commit.message)




    def show_commit_context_menu(self, position):
        row = self.history_table.rowAt(position.y())
        if row == -1:
            return

        self.history_table.selectRow(row)

        # Get commit SHA from tooltip in column 1 (set in update_log)
        commit_item = self.history_table.item(row, 1)
        if not commit_item:
            return

        commit_sha = commit_item.toolTip()

        menu = QMenu(self)
        delete_action = QAction("🗑️ Delete This Snapshot", self)

        # Check if commit is reachable from current branch
        try:
            reachable = [c.hexsha for c in self.repo.iter_commits()]
            if commit_sha not in reachable:
                delete_action.setEnabled(False)
                delete_action.setToolTip("❌ This commit is from another version line.")
        except Exception as e:
            print(f"[WARN] Could not validate commit reachability: {e}")

        delete_action.triggered.connect(self.delete_selected_commit)
        menu.addAction(delete_action)
        menu.exec(self.history_table.viewport().mapToGlobal(position))


    def update_version_line_label(self):
        if not hasattr(self, "version_line_label"):
            return

        try:
            branch_name = self.repo.active_branch.name
            self.version_line_label.setText(f"🎚️ You’re working on version line: {branch_name}")
        except Exception:
            self.version_line_label.setText("🎧 Snapshot mode: no active version line")


    def delete_selected_commit(self):
        row = self.history_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a snapshot to delete.")
            return

        commit_id = self.history_table.item(row, 1).toolTip()
        commit_msg = self.history_table.item(row, 2).text()

        confirm = QMessageBox.question(
            self,
            "Delete Snapshot?",
            "🗑️ Are you sure you want to delete this snapshot from your project's timeline?\n\n"
            "This action is permanent and cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            # Backup first (optional but recommended)
            if self.has_unsaved_changes():
                self.backup_unsaved_changes()

            # Rebase interactively to drop the selected commit
            all_commits = list(self.repo.iter_commits("HEAD", max_count=50))
            target_commit = next((c for c in all_commits if c.hexsha.startswith(commit_id[:7])), None)

            if not target_commit:
                raise Exception("Commit not found in history.")

            base = all_commits[all_commits.index(target_commit) + 1]  # commit just after the one being deleted
            subprocess.run(
                ["git", "rebase", "--onto", base.hexsha, target_commit.hexsha],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            # Refresh UI
            self.init_git()

            # Auto-select nearest commit (base), scroll to it
            self.current_commit_id = base.hexsha
            self.update_log()
            self.history_table.scrollToItem(self.history_table.item(0, 0), QTableWidget.ScrollHint.PositionAtTop)

            # Automatically check out that commit
            self.repo.git.checkout(base.hexsha)
            self.current_commit_id = base.hexsha
            self.status_message(f"Snapshot deleted. Now viewing: {base.hexsha[:7]}")
            self.show_commit_checkout_info(self.repo.commit(base.hexsha))

            # Open the DAW project
            self.open_latest_daw_project()

        except Exception as e:
            QMessageBox.critical(self, "Delete Failed", f"Failed to delete commit:\n{e}")


    def open_latest_daw_project(self):
        """🎛️ Reopen the main DAW project file from the working directory."""
        try:
            daw_files = list(self.project_path.glob("*.als")) + list(self.project_path.glob("*.logicx"))
            if not daw_files:
                QMessageBox.information(
                    self,
                    "No DAW File Found",
                    "🎚️ We couldn’t find an Ableton (.als) or Logic (.logicx) file in this version.\n\n"
                    "Make sure your project file is saved in the selected folder."
                )
                return

            daw_file = daw_files[0]  # Open the first matching file

            # 🔁 Use Popen here so the test can mock it directly
            subprocess.Popen(["open", str(daw_file)])
            print(f"🎼 Reopened DAW project: {daw_file.name}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Couldn’t Open Project",
                f"❌ Something went wrong while launching your DAW file:\n\n{e}"
            )



    def rebase_delete_commit(self, commit_id):
        try:
            reachable_commits = [c.hexsha for c in self.repo.iter_commits()]
            try:
                current_branch = self.repo.active_branch.name
            except TypeError:
                current_branch = "detached HEAD"

            QMessageBox.information(
                self, "DEBUG",
                f"🧠 Trying to delete commit: {commit_id[:10]}\n"
                f"🌿 Current branch: {current_branch}\n\n"
                f"📜 Reachable commits:\n" + "\n".join(c[:10] for c in reachable_commits)
            )

            if commit_id not in reachable_commits:
                QMessageBox.warning(
                    self,
                    "Can't Delete Snapshot",
                    "🎚️ You’re trying to delete a snapshot from another version line.\n\n"
                    "Switch to that version first if you still want to remove it."
                )

                return

            # ✅ Do the rebase
            subprocess.run(
                ["git", "rebase", "--onto", f"{commit_id}^", commit_id],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            self.init_git()
            self.update_log()
            self.open_latest_daw_project()

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Rebase Failed", f"Git error:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"❌ {e}")



    def show_commit_checkout_info(self, commit):
        if not self.repo or not commit:
            return

        commits = list(self.repo.iter_commits(max_count=50))
        commits.reverse()  # ✅ To match UI row order

        index = next((i for i, c in enumerate(commits) if c.hexsha == commit.hexsha), None)
        age_str = "(latest)" if index == 0 else f"({index} commits ago)" if index is not None else "(older)"

        short_msg = commit.message.strip().split("\n")[0][:40]
        short_hash = commit.hexsha[:7]

        label = f"[#{index + 1 if index is not None else '?'} - {short_hash}] - {short_msg} {age_str}"
        timestamp = commit.committed_datetime.strftime("%d %b %Y, %H:%M")

        body = f"{label}\n\n" + ("-" * 40) + f"\n\nCommitted: {timestamp}"

        if self.repo.head.is_detached:
            body += (
                "\n\n📦 You’re now viewing a snapshot of your project.\n"
                "This version is locked (read-only).\n\n"
                "🎼 To make changes, start a new version line from here."
            )
            title = "Viewing Snapshot"
        else:
            title = "Switched Version"

        QMessageBox.information(self, title, body)
    

    def auto_commit(self, message: str, tag: str = ""):
        if not self.repo:
            QMessageBox.warning(
                self,
                "No Repo",
                "🎛️ Please initialize version control before saving your project."
            )
            return

        try:
            subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)

            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(
                    self,
                    "No Changes",
                    "✅ No changes found — your project is already up to date."
                )
                return

            commit = self.repo.index.commit(message)

            if tag:
                if tag in [t.name for t in self.repo.tags]:
                    print(f"⚠️ Tag '{tag}' already exists. Skipping tag creation.")
                else:
                    self.repo.create_tag(tag, ref=commit.hexsha)

            if self.remote_checkbox.isChecked():
                try:
                    subprocess.run(
                        ["git", "push", "origin", self.get_default_branch(), "--tags"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        check=True
                    )
                except subprocess.CalledProcessError:
                    print("[WARN] Skipping remote push: no remote set")

            self.update_log()
            msg = f"✅ Auto-commit completed:\n\n{message}"
            QMessageBox.information(
                self,
                "Auto Save Complete",
                msg
            )
            print(f"✅ Auto-committed: {message}")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Auto Commit Failed",
                f"❌ Something went wrong while saving your version:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Auto Commit Failed",
                f"⚠️ Unexpected error while saving your session:\n\n{e}"
            )


    def is_commit_deletable(self, commit_id):
        """Returns True if the commit can be deleted from the current branch"""
        try:
            # Check if commit is in current branch history
            reachable = commit_id in [c.hexsha for c in self.repo.iter_commits()]
            if not reachable:
                return False

            # Check if it's a protected commit (🎼 marker)
            commit_msg = self.repo.commit(commit_id).message
            if "🎼" in commit_msg:
                return False

            return True
        except Exception:
            return False
            

    def checkout_selected_commit(self, commit_sha=None):
        if commit_sha:
            try:
                subprocess.run(
                    ["git", "reset", "--hard", commit_sha],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )
                subprocess.run(
                    ["git", "lfs", "checkout"],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )
                self.repo = Repo(self.project_path)
                self.current_commit_id = self.repo.head.commit.hexsha
                self.init_git()
                self.update_log()
                self.show_commit_checkout_info(self.repo.commit(commit_sha))
            except Exception as e:
                QMessageBox.critical(self, "Checkout Failed", f"❌ Checkout failed:\n\n{e}")
            return

        # GUI-based selection
        selected_row = self.history_table.currentRow()
        if selected_row < 0:
            return

        commit_item = self.history_table.item(selected_row, 1)
        if not commit_item:
            return

        commit_sha = commit_item.toolTip()

        try:
            # 🔐 Ask about unsaved changes
            if self.has_unsaved_changes():
                choice = QMessageBox.question(
                    self,
                    "Unsaved Changes Detected",
                    "🎚️ You have unsaved or modified files.\n\n"
                    "Would you like to back up your project before switching versions?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if choice == QMessageBox.StandardButton.Yes:
                    self.backup_unsaved_changes()

                subprocess.run(
                    ["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )

            # ✅ SAFETY CHECK: Only reset if detached
            if self.repo.head.is_detached:
                subprocess.run(
                    ["git", "reset", "--hard", commit_sha],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )
            else:
                subprocess.run(
                    ["git", "checkout", commit_sha],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )

            subprocess.run(
                ["git", "lfs", "checkout"],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            self.repo = Repo(self.project_path)
            self.current_commit_id = self.repo.head.commit.hexsha
            self.init_git()
            self.update_log()
            self.show_commit_checkout_info(self.repo.commit(commit_sha))

            QMessageBox.information(
                self,
                "Project Restored",
                "✅ This version of your project has been restored.\n\n"
                "📂 Please re-open the .als file in Ableton to view the changes."
            )
            self.open_als_button.setVisible(True)

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Checkout Failed", f"❌ Could not switch to the selected version:\n\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"⚠️ Something unexpected happened:\n\n{e}")
          

    def switch_version_line(self):
        if not self.repo:
            QMessageBox.warning(
                self,
                "No Project Loaded",
                "🎛️ Please load or set up a project folder first."
            )
            return

        try:
            branches = [head.name for head in self.repo.heads]
            if not branches:
                QMessageBox.information(
                    self,
                    "No Saved Versions",
                    "🎚️ This project doesn’t have any saved version lines yet.\n\nYou can create one using 'Start New Version Line'."
                )
                return

            if self.repo.head.is_detached:
                confirm = QMessageBox.question(
                    self,
                    "Currently in Snapshot View",
                    "🎧 You’re currently exploring a snapshot of your project.\n\n"
                    "Switching versions now will load the selected version line.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )
                if confirm != QMessageBox.StandardButton.Yes:
                    return

            selected, ok = QInputDialog.getItem(
                self,
                "🎚 Switch Version Line",
                "Choose a version line to switch to:",
                branches,
                editable=False
            )
            if ok and selected:
                if self.has_unsaved_changes():
                    if QMessageBox.question(
                        self,
                        "Unsaved Changes Detected",
                        "🎵 You’ve made changes that aren’t saved to a version yet.\n\nWould you like to back them up before switching?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    ) == QMessageBox.StandardButton.Yes:
                        self.backup_unsaved_changes()
                    subprocess.run(
                        ["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        check=True
                    )

                self.repo.git.checkout(selected)
                self.current_commit_id = self.repo.head.commit.hexsha
                self.update_log()
                self.status_message(f"🎚 Switched to version line: {selected}")
                latest_commit = self.repo.head.commit
                self.show_commit_checkout_info(latest_commit)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Switch Failed",
                f"❌ Couldn’t switch version lines:\n\n{e}"
            )


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
                QMessageBox.warning(
                    self,
                    "No Project",
                    "🎛️ No project folder is currently loaded.\n\nPlease select or set up a project first."
                )
                return

            target_dir = QFileDialog.getExistingDirectory(self, "Select Folder to Save Snapshot")
            if not target_dir:
                return

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            snapshot_name = f"{self.project_path.name}_snapshot_{timestamp}"
            dest = os.path.join(target_dir, snapshot_name)

            for item in os.listdir(self.project_path):
                if item == ".git":
                    continue  # 🚫 Skip Git internals
                src = os.path.join(self.project_path, item)
                dst = os.path.join(dest, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)

            QMessageBox.information(
                self,
                "Snapshot Exported",
                f"📦 A snapshot of your project has been saved to:\n\n{dest}"
            )

        except Exception as e:
            print("❌ Error during snapshot export:")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Export Failed",
                f"⚠️ Something went wrong while exporting your snapshot:\n\n{e}"
            )


    def import_snapshot(self):
        import traceback
        try:
            src_folder = QFileDialog.getExistingDirectory(self, "Select Snapshot Folder to Import")
            if not src_folder:
                return

            target_path = self.project_path
            if not target_path or not target_path.exists():
                QMessageBox.warning(
                    self,
                    "Invalid Project",
                    "🎛️ Please load a valid project folder before importing a snapshot."
                )
                return

            for item in os.listdir(src_folder):
                if item == ".git":
                    continue  # 🚫 Never import Git folder

                s = os.path.join(src_folder, item)
                d = os.path.join(target_path, item)

                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            QMessageBox.information(
                self,
                "Snapshot Imported",
                f"📂 Your snapshot has been added to:\n\n{target_path}"
            )
            self.init_git()

        except Exception as e:
            print("❌ Error during snapshot import:")
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Import Failed",
                f"⚠️ Something went wrong while importing your snapshot:\n\n{e}"
            )


        
    def checkout_commit(self, commit_sha):
        import shutil
        import datetime

        try:
            if self.repo.untracked_files:
                return {
                    "status": "warning",
                    "message": f"Untracked files exist: {self.repo.untracked_files}"
                }

            # Backup before checkout
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.repo_path.parent / f"Backup_{self.repo_path.name}_{timestamp}"
            shutil.copytree(self.repo_path, backup_dir)
            print(f"🔒 Unsaved changes backed up to: {backup_dir}")

            self.repo.git.checkout(commit_sha)
            self.refresh_commit_history()

            return {
                "status": "success",
                "message": f"Checked out commit {commit_sha}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


    def highlight_current_commit(self):
        try:
            current_commit = self.repo.head.commit.hexsha[:7]
            self.current_commit_id = self.repo.head.commit.hexsha
            self.update_log()

            QMessageBox.information(
                self,
                "Current Version",
                f"✅ You’re currently on version:\n\n🔖 {current_commit}"
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Couldn’t Highlight",
                f"⚠️ We couldn’t locate your current version in the history:\n\n{e}"
            )


    def clear_highlight_on_click(self):
        self.current_commit_id = None


    def start_new_version_line(self):
        raw_input, ok = QInputDialog.getText(
            self,
            "🎼 Start New Version Line",
            "Name your new version line (e.g. 'alt_take2', 'live_mix', or 'idea_bounce'):\n\n"
            "✅ Use letters, numbers, dashes, or underscores.\n"
            "🚫 Avoid spaces, slashes, or special characters."
        )

        if ok:
            # ✅ Clean and validate input
            branch_name = raw_input.strip().lower().replace(" ", "_")
            branch_name = "".join(c for c in branch_name if c.isalnum() or c in ("_", "-"))

            if not branch_name:
                QMessageBox.warning(
                    self,
                    "Invalid Name",
                    "❌ Please enter a valid name using only letters, numbers, dashes, or underscores."
                )
                return

            try:
                if branch_name in [h.name for h in self.repo.heads]:
                    QMessageBox.warning(
                        self,
                        "Version Line Exists",
                        f"⚠️ A version line called '{branch_name}' already exists.\n\nPlease choose a different name."
                    )
                    return

                commit_hash = self.repo.head.commit.hexsha
                subprocess.run(
                    ["git", "checkout", "-b", branch_name, commit_hash],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )

                # 🏷 Optional marker commit
                marker_file = self.project_path / ".dawgit_version_stamp"
                marker_file.write_text(f"Start of {branch_name}", encoding="utf-8")
                subprocess.run(["git", "add", marker_file.name], cwd=self.project_path, check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"🎼 Start new version line: {branch_name}"],
                    cwd=self.project_path,
                    check=True
                )

                QMessageBox.information(
                    self,
                    "Version Line Created",
                    f"🌱 You’re now working on version line:\n\n{branch_name}"
                )

            except subprocess.CalledProcessError as e:
                QMessageBox.critical(
                    self,
                    "Error Creating Version",
                    f"❌ Could not create version line:\n\n{e}"
                )


    def switch_branch(self):
        if not self.repo:
            QMessageBox.warning(
                self,
                "Project Not Set Up",
                "🎛️ Please load or set up a project folder first."
            )
            return

        try:
            branches = [head.name for head in self.repo.heads]
            if not branches:
                QMessageBox.information(
                    self,
                    "No Saved Versions",
                    "🎚️ This project has no saved version lines yet.\n\nUse 'Start New Version Line' to begin branching."
                )
                return

            if self.repo.head.is_detached:
                # 🎧 Warn about switching from snapshot view
                choice = QMessageBox.question(
                    self,
                    "Currently Viewing Snapshot",
                    "🎧 You’re currently exploring a snapshot.\n\n"
                    "Switching now will move you to a saved version line.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )
                if choice != QMessageBox.StandardButton.Yes:
                    return

            selected_branch, ok = QInputDialog.getItem(
                self,
                "🔀 Switch to Saved Version",
                "Choose a saved version line:",
                branches,
                editable=False
            )
            if not ok or not selected_branch:
                return

            if self.has_unsaved_changes():
                choice = QMessageBox.question(
                    self,
                    "Unsaved Work Detected",
                    "🎵 You’ve made changes that haven’t been saved yet.\n\nWould you like to back them up before switching?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if choice == QMessageBox.StandardButton.Yes:
                    self.backup_unsaved_changes()

                subprocess.run(
                    ["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )

            subprocess.run(
                ["git", "checkout", selected_branch],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            self.init_git()
            QMessageBox.information(
                self,
                "Switched Version",
                f"🎚️ You’re now working on version line:\n\n{selected_branch}"
            )

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Couldn’t Switch",
                f"❌ Something went wrong switching versions:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Unexpected Issue",
                f"⚠️ Something unexpected happened:\n\n{e}"
            )


    def switch_branch(self):
        if not self.repo:
            QMessageBox.warning(
                self,
                "Project Not Set Up",
                "🎛️ Please load or set up a project folder first."
            )
            return

        try:
            branches = [head.name for head in self.repo.heads]
            if not branches:
                QMessageBox.information(
                    self,
                    "No Saved Versions",
                    "🎚️ This project has no saved version lines yet.\n\nUse 'Start New Version Line' to begin branching."
                )
                return

            if self.repo.head.is_detached:
                # 🎧 Warn about switching from snapshot view
                choice = QMessageBox.question(
                    self,
                    "Currently Viewing Snapshot",
                    "🎧 You’re currently exploring a snapshot.\n\n"
                    "Switching now will move you to a saved version line.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )
                if choice != QMessageBox.StandardButton.Yes:
                    return

            selected_branch, ok = QInputDialog.getItem(
                self,
                "🔀 Switch to Saved Version",
                "Choose a saved version line:",
                branches,
                editable=False
            )
            if not ok or not selected_branch:
                return

            if self.has_unsaved_changes():
                choice = QMessageBox.question(
                    self,
                    "Unsaved Work Detected",
                    "🎵 You’ve made changes that haven’t been saved yet.\n\nWould you like to back them up before switching?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if choice == QMessageBox.StandardButton.Yes:
                    self.backup_unsaved_changes()

                subprocess.run(
                    ["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )

            subprocess.run(
                ["git", "checkout", selected_branch],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            self.init_git()
            QMessageBox.information(
                self,
                "Switched Version",
                f"🎚️ You’re now working on version line:\n\n{selected_branch}"
            )

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Couldn’t Switch",
                f"❌ Something went wrong switching versions:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Unexpected Issue",
                f"⚠️ Something unexpected happened:\n\n{e}"
            )


    def checkout_latest(self):
        try:
            # 🔐 Safety: Prompt if unsaved changes exist
            if self.has_unsaved_changes():
                choice = QMessageBox.question(
                    self,
                    "Unsaved Changes Detected",
                    "🎚️ You have unsaved or modified files.\n\n"
                    "Would you like to back up your project before returning to the latest saved version?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if choice == QMessageBox.StandardButton.Yes:
                    self.backup_unsaved_changes()

                subprocess.run(
                    ["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )

            # ✅ Checkout main branch
            subprocess.run(
                ["git", "checkout", self.get_default_branch()],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            latest_commit = next(self.repo.iter_commits(self.get_default_branch(), max_count=1))
            self.current_commit_id = latest_commit.hexsha

            self.update_log()
            self.status_message("Returned to latest version (main branch)")
            self.show_commit_checkout_info(latest_commit)

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Checkout Error",
                f"❌ Couldn’t return to the latest version line:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"⚠️ Something unexpected happened:\n\n{e}"
            )



    def open_project_folder(self, event):
        if self.project_path.exists():
            subprocess.run(["open", str(self.project_path)])

    def clear_saved_project(self):
        if self.settings_path.exists():
            try:
                self.settings_path.unlink()
                QMessageBox.information(
                    self,
                    "Project Path Cleared",
                    "🧹 Your saved project path has been cleared.\n\n"
                    "Next time you open the app, it will default to your current folder."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Clearing Path",
                    f"❌ Something went wrong while clearing your saved path:\n\n{e}"
                )
        else:
            QMessageBox.information(
                self,
                "No Saved Path",
                "ℹ️ No saved project path found to clear."
            )


    def auto_commit(self, message: str, tag: str = ""):
        if not self.repo:
            QMessageBox.warning(
                self,
                "No Repo",
                "🎛️ Please initialize version control before saving your project."
            )
            return

        try:
            subprocess.run(["git", "add", "-A"], cwd=self.project_path, env=self.custom_env(), check=True)

            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(
                    self,
                    "No Changes",
                    "✅ No changes found — your project is already up to date."
                )
                return

            commit = self.repo.index.commit(message)

            if tag:
                if tag in [t.name for t in self.repo.tags]:
                    print(f"⚠️ Tag '{tag}' already exists. Skipping tag creation.")
                else:
                    self.repo.create_tag(tag, ref=commit.hexsha)

            if self.remote_checkbox.isChecked():
                try:
                    subprocess.run(
                        ["git", "push", "origin", self.get_default_branch(), "--tags"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        check=True
                    )
                except subprocess.CalledProcessError:
                    print("[WARN] Skipping remote push: no remote set")

            self.update_log()
            msg = f"✅ Auto-commit completed:\n\n{message}"
            QMessageBox.information(
                self,
                "Auto Save Complete",
                msg
            )
            print(f"✅ Auto-committed: {message}")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Auto Commit Failed",
                f"❌ Something went wrong while saving your version:\n\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Auto Commit Failed",
                f"⚠️ Unexpected error while saving your session:\n\n{e}"
            )



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
        if not self.repo:
            return
        if hasattr(self, "unsaved_indicator"):
            self.unsaved_indicator.setVisible(
                self.repo.is_dirty(index=True, working_tree=True, untracked_files=True)
            )


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
    
    def launch_file_with_system(self, file_path):
        subprocess.Popen(["open", str(file_path)])



    def open_daw_project(self):
        if not self.project_path:
            return

        als_file = next(self.project_path.glob("*.als"), None)
        logicx_file = next(self.project_path.glob("*.logicx"), None)
        daw_file = als_file or logicx_file

        if daw_file and daw_file.exists():
            try:
                subprocess.run(["open", str(daw_file)], check=True)
                print(f"🎼 Opening DAW file: {daw_file.name}")
            except Exception as e:
                print(f"❌ Failed to open DAW project file: {e}")

    def show_status_message(self, message):
        """🎵 Display a status message to the user in the status label."""
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Status: {message}")
        else:
            print(f"[STATUS] {message}")
            

    def _show_info(self, message):
        QMessageBox.information(self, "Heads up", message)


    def _show_warning(self, message):
        QMessageBox.warning(self, "Heads up", message)


    def _show_error(self, message):
        QMessageBox.critical(self, "Something went wrong", message)



# Handle Ctrl+C gracefully
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DAWGitApp()
    win.show()
    sys.exit(app.exec())

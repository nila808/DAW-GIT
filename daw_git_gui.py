#!/usr/bin/env python3
import os
import sys
import subprocess

# --- PyQt6 ---
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox, QLineEdit
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

# --- GitPython ---
from git import Repo, InvalidGitRepositoryError, NoSuchPathError

# --- PATH FIX for Bundled Apps ---
if getattr(sys, 'frozen', False):
    os.environ["PATH"] = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]

class DAWGitGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = None
        self.project_path = os.getcwd()

        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(self.base_path, "icon.png")

        # --- Window Settings ---
        self.setWindowTitle("DAW Git Version Control")
        self.setGeometry(300, 300, 900, 800)
        self.setWindowIcon(QIcon(icon_path))

        # --- Main Layout ---
        main_layout = QVBoxLayout()

        # --- Logo ---
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setPixmap(QPixmap(icon_path).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(self.logo_label)

        # --- Theme Section ---
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout()

        self.theme_label = QLabel("Select Theme:")
        theme_layout.addWidget(self.theme_label)

        self.theme_picker = QComboBox()
        self.theme_picker.addItems(["Dark", "Light", "Funky"])
        self.theme_picker.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_picker)

        self.reload_style_button = QPushButton("Reload Style")
        self.reload_style_button.setObjectName("reloadButton")
        self.reload_style_button.clicked.connect(self.reload_styles)
        self.reload_style_button.setMinimumHeight(40)
        self.reload_style_button.setMinimumWidth(200)
        theme_layout.addWidget(self.reload_style_button)

        theme_group.setLayout(theme_layout)
        theme_group.setMinimumHeight(150)
        main_layout.addWidget(theme_group)

        # --- Project Setup Section ---
        setup_group = QGroupBox("Project Setup")
        setup_layout = QVBoxLayout()

        self.setup_button = QPushButton("Setup Project")
        self.setup_button.setObjectName("setupButton")
        self.setup_button.clicked.connect(self.run_setup_wizard)
        setup_layout.addWidget(self.setup_button)

        self.remote_checkbox = QCheckBox("Enable remote push (cloud sync)")
        setup_layout.addWidget(self.remote_checkbox)

        setup_group.setLayout(setup_layout)
        main_layout.addWidget(setup_group)

        # --- NEW Advanced Git Tools Section ---
        advanced_group = QGroupBox("Advanced Git Tools")
        advanced_layout = QVBoxLayout()

        # Git Status
        self.status_label = QLabel("Repository Status: Unknown")
        advanced_layout.addWidget(self.status_label)

        # Branch Selector
        self.branch_combo = QComboBox()
        advanced_layout.addWidget(self.branch_combo)

        self.switch_branch_button = QPushButton("Switch Branch")
        self.switch_branch_button.clicked.connect(self.switch_branch)
        advanced_layout.addWidget(self.switch_branch_button)

        # Remote Setup
        self.remote_url_input = QLineEdit()
        self.remote_url_input.setPlaceholderText("Enter remote repository URL")
        advanced_layout.addWidget(self.remote_url_input)

        self.set_remote_button = QPushButton("Set Remote URL")
        self.set_remote_button.clicked.connect(self.set_remote)
        advanced_layout.addWidget(self.set_remote_button)

        advanced_group.setLayout(advanced_layout)
        main_layout.addWidget(advanced_group)

        # --- Status Display ---
        self.status = QLabel("Initializing...")
        main_layout.addWidget(self.status)

        # --- Commit Section (will continue in Part 2) ---

        # --- Commit Section ---
        commit_group = QGroupBox("Commit Changes")
        commit_layout = QVBoxLayout()

        self.commit_message_label = QLabel("Commit Message:")
        commit_layout.addWidget(self.commit_message_label)

        self.commit_message = QTextEdit()
        self.commit_message.setPlaceholderText("Enter commit message...")
        commit_layout.addWidget(self.commit_message)

        self.tag_input_label = QLabel("Tag (optional):")
        commit_layout.addWidget(self.tag_input_label)

        self.tag_input = QTextEdit()
        self.tag_input.setPlaceholderText("Enter tag (e.g., 'Mix 1', 'Final Master')")
        self.tag_input.setMaximumHeight(40)
        commit_layout.addWidget(self.tag_input)

        self.commit_button = QPushButton("Commit Changes")
        self.commit_button.setObjectName("commitButton")
        self.commit_button.clicked.connect(self.commit_changes)
        commit_layout.addWidget(self.commit_button)

        self.view_changes_button = QPushButton("View Unstaged Changes")
        self.view_changes_button.setObjectName("viewChangesButton")
        self.view_changes_button.clicked.connect(self.view_changes)
        commit_layout.addWidget(self.view_changes_button)

        self.view_staged_changes_button = QPushButton("View Staged Changes")
        self.view_staged_changes_button.setObjectName("viewStagedChangesButton")
        self.view_staged_changes_button.clicked.connect(self.view_staged_changes)
        commit_layout.addWidget(self.view_staged_changes_button)

        commit_group.setLayout(commit_layout)
        main_layout.addWidget(commit_group)

        # --- Commit History Section ---
        history_group = QGroupBox("Commit History")
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Tag", "Commit ID", "Message"])
        history_layout.addWidget(self.history_table)

        buttons_layout = QHBoxLayout()

        self.checkout_button = QPushButton("Checkout Selected Version")
        self.checkout_button.setObjectName("checkoutButton")
        self.checkout_button.clicked.connect(self.checkout_selected_commit)
        buttons_layout.addWidget(self.checkout_button)

        self.return_latest_button = QPushButton("Return to Latest Version")
        self.return_latest_button.setObjectName("returnButton")
        self.return_latest_button.clicked.connect(self.return_to_latest)
        buttons_layout.addWidget(self.return_latest_button)

        history_layout.addLayout(buttons_layout)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)

        # --- Set Main Layout ---
        self.setLayout(main_layout)

        # --- Initial Setup ---
        self.apply_theme("Dark")
        self.init_git()

    # --- Theme Applying ---
    def apply_theme(self, theme_name="Dark"):
        print(f"Applying theme: {theme_name}")
        theme_name = theme_name.lower()
        file_mapping = {
            "dark": "dark_theme.qss",
            "light": "light_theme.qss",
            "funky": "funky_theme.qss"
        }
        theme_file = file_mapping.get(theme_name)

        if theme_file:
            if getattr(sys, 'frozen', False):
                bundle_dir = os.path.abspath(os.path.dirname(sys.executable))
                base_path = os.path.join(bundle_dir, "styles")
            else:
                base_path = os.path.join(os.path.dirname(__file__), "styles")

            qss_path = os.path.join(base_path, theme_file)
            print(f"Loading QSS from: {qss_path}")

            if os.path.exists(qss_path):
                try:
                    with open(qss_path, "r") as f:
                        qss = f.read()
                    QApplication.instance().setStyleSheet(qss)
                    self.setStyleSheet(qss)
                    print("✅ Stylesheet applied.")
                except Exception as e:
                    print(f"❗ Error applying stylesheet: {e}")
            else:
                print(f"❗ Theme file not found: {qss_path}")

    def reload_styles(self):
        print("Reloading styles...")
        app = QApplication.instance()
        app.setStyleSheet("")
        self.setStyleSheet("")
        QApplication.processEvents()
        self.apply_theme(self.theme_picker.currentText())
        self.style().polish(self)
        self.update()
        self.repaint()
        QApplication.processEvents()
        QMessageBox.information(self, "Reloaded", "✅ Styles reloaded successfully.")

    # --- Git Initialization ---
    def init_git(self):
        try:
            self.repo = Repo(self.project_path)
            self.status.setText(f"Git repository detected at: {self.project_path}")
            self.update_branches()
            self.update_log()
            self.update_repo_status()
        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repo = None
            self.status.setText("No Git repository found. Please run setup.")

    # --- Git Branch Handling ---
    def update_branches(self):
        if not self.repo:
            return
        self.branch_combo.clear()
        for branch in self.repo.branches:
            self.branch_combo.addItem(branch.name)

    def switch_branch(self):
        if not self.repo:
            return
        selected_branch = self.branch_combo.currentText()
        try:
            self.repo.git.checkout(selected_branch)
            self.status.setText(f"Switched to branch {selected_branch}")
            self.update_log()
            self.update_repo_status()
        except Exception as e:
            QMessageBox.critical(self, "Branch Switch Failed", str(e))

    # --- Set Remote URL ---
    def set_remote(self):
        if not self.repo:
            return
        url = self.remote_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter a remote repository URL.")
            return
        try:
            if 'origin' in self.repo.remotes:
                self.repo.delete_remote('origin')
            self.repo.create_remote('origin', url)
            self.status.setText(f"Remote set to {url}")
        except Exception as e:
            QMessageBox.critical(self, "Remote Setup Failed", str(e))

    # --- Update Repo Status ---
    def update_repo_status(self):
        if not self.repo:
            return
        if self.repo.is_dirty(untracked_files=True):
            staged = self.repo.git.diff('--cached')
            if staged:
                self.status_label.setText("Repository Status: ❗️ Staged but Uncommitted Changes")
                self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setText("Repository Status: ⚠️ Unstaged Changes Present")
                self.status_label.setStyleSheet("color: orange;")
        else:
            self.status_label.setText("Repository Status: ✅ Clean")
            self.status_label.setStyleSheet("color: green;")

    # --- Git Setup Wizard ---
    def run_setup_wizard(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_path = folder
            os.chdir(folder)
            self.setup_git()
            self.init_git()

    def setup_git(self):
        subprocess.run(["git", "init"])
        subprocess.run(["git", "lfs", "install"])
        with open(".gitattributes", "w") as f:
            for ext in [
                "*.als", "*.logicx", "*.wav", "*.aif", "*.aiff",
                "*.flac", "*.mp3", "*.ogg", "*.nki", "*.nkm", "*.exs"
            ]:
                f.write(f"{ext} filter=lfs diff=lfs merge=lfs -text\n")
        with open(".gitignore", "w") as f:
            f.write("""*.als~\n*.logicx~\n*.asd\n*.bak\n*.tmp\nBackup/\nBounces/\nFreeze Files/\nRender/\nCache/\nAudio Files/\nSamples/\n.DS_Store\nThumbs.db\n""")
        QMessageBox.information(self, "Setup Complete", "Git + LFS Initialized!")

    # --- Git Commit ---
    def commit_changes(self):
        if not self.repo:
            QMessageBox.warning(self, "Error", "This folder is not a Git repository.")
            return
        msg = self.commit_message.toPlainText().strip()
        tag = self.tag_input.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Missing Message", "Please enter a commit message.")
            return
        try:
            self.repo.git.add(A=True)
            if not self.repo.is_dirty(index=True, working_tree=True, untracked_files=True):
                QMessageBox.information(self, "No Changes", "No new changes to commit.")
                return
            new_commit = self.repo.index.commit(msg)
            if tag:
                self.repo.create_tag(tag, ref=new_commit.hexsha)
            if self.remote_checkbox.isChecked():
                try:
                    origin = self.repo.remote(name='origin')
                    origin.push()
                    origin.push("--tags")
                except Exception as e:
                    self.status.setText(f"Push failed: {e}")
            self.update_log()
            self.commit_message.clear()
            self.tag_input.clear()
            self.update_repo_status()
            self.status.setText("Committed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Commit Failed", str(e))

    # --- View Changes ---
    def view_changes(self):
        if not self.repo:
            QMessageBox.warning(self, "Error", "No Git repository found.")
            return
        try:
            diff_output = self.repo.git.diff()
            self.show_diff_popup(diff_output, "Unstaged Changes")
        except Exception as e:
            QMessageBox.critical(self, "View Changes Failed", str(e))

    def view_staged_changes(self):
        if not self.repo:
            QMessageBox.warning(self, "Error", "No Git repository found.")
            return
        try:
            diff_output = self.repo.git.diff('--cached')
            self.show_diff_popup(diff_output, "Staged Changes")
        except Exception as e:
            QMessageBox.critical(self, "View Staged Changes Failed", str(e))

    def show_diff_popup(self, diff_output, title):
        if not diff_output.strip():
            QMessageBox.information(self, title, "No changes to show.")
            return

        diff_window = QTextEdit()
        diff_window.setReadOnly(True)
        diff_window.setPlainText(diff_output)

        diff_popup = QWidget()
        diff_popup.setWindowTitle(title)
        diff_layout = QVBoxLayout()
        diff_layout.addWidget(diff_window)
        diff_popup.setLayout(diff_layout)
        diff_popup.resize(700, 500)
        diff_popup.show()

        self.diff_popup = diff_popup

    # --- Update Commit History ---
    def update_log(self):
        self.history_table.setRowCount(0)
        if not self.repo:
            return
        commits = list(self.repo.iter_commits('HEAD', max_count=50))
        tags = {tag.commit.hexsha: tag.name for tag in self.repo.tags}
        for i, commit in enumerate(commits):
            self.history_table.insertRow(i)
            tag_name = tags.get(commit.hexsha, "")
            self.history_table.setItem(i, 0, QTableWidgetItem(tag_name))
            self.history_table.setItem(i, 1, QTableWidgetItem(commit.hexsha[:7]))
            self.history_table.setItem(i, 2, QTableWidgetItem(commit.message.strip()))

    # --- Checkout Commit ---
    def checkout_selected_commit(self):
        if not self.repo:
            return
        selected_row = self.history_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a commit first.")
            return
        selected_commit_id = self.history_table.item(selected_row, 1).text()
        if self.repo.is_dirty(untracked_files=True):
            if QMessageBox.question(self, "Uncommitted Changes", "Changes exist! Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
        try:
            self.repo.git.checkout(selected_commit_id)
            self.update_log()
            self.update_repo_status()
            self.status.setText(f"Checked out {selected_commit_id}")
        except Exception as e:
            QMessageBox.critical(self, "Checkout Failed", str(e))

    def return_to_latest(self):
        if not self.repo:
            return
        if self.repo.is_dirty(untracked_files=True):
            if QMessageBox.question(self, "Uncommitted Changes", "Changes exist! Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
        try:
            if "main" in self.repo.heads:
                self.repo.git.checkout("main")
            elif "master" in self.repo.heads:
                self.repo.git.checkout("master")
            else:
                QMessageBox.warning(self, "No Branch", "No 'main' or 'master' branch.")
                return
            self.update_log()
            self.update_repo_status()
            self.status.setText("Returned to latest version.")
        except Exception as e:
            QMessageBox.critical(self, "Checkout Failed", str(e))

# --- Main Program Launcher ---
if __name__ == "__main__":
    app = QApplication([])
    window = DAWGitGUI()
    window.show()
    app.exec()

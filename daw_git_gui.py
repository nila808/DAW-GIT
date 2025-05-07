#!/usr/bin/env python3
import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from git import Repo, InvalidGitRepositoryError, NoSuchPathError

# ✅ PATH FIX: Bundle apps need correct path for Git LFS
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

        self.setWindowTitle("DAW Git Version Control")
        # Application Dimensions
        self.setGeometry(300, 300, 600, 700)
        self.setWindowIcon(QIcon(icon_path))

        main_layout = QVBoxLayout()

        # Logo Area
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setPixmap(QPixmap(icon_path).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio))
        main_layout.addWidget(self.logo_label)

        # Theme Section
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
        theme_layout.addWidget(self.reload_style_button)

        theme_group.setLayout(theme_layout)
        main_layout.addWidget(theme_group)

        # Setup Section
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

        # Status Label
        self.status = QLabel("Initializing...")
        main_layout.addWidget(self.status)

        # Commit Section
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

        # Commit History Section
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

        self.setLayout(main_layout)

        self.apply_theme("Dark")
        self.init_git()

    # --- Methods ---

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
                    self.setStyleSheet(qss)
                    QApplication.instance().setStyleSheet(qss)
                    print("✅ StyleSheet applied successfully to app.")
                except Exception as e:
                    print(f"❗ Error applying StyleSheet: {e}")
            else:
                print(f"❗ Warning: Theme file not found: {qss_path}")




    def change_theme(self, text):
        self.apply_theme(text)

    def reload_styles(self):
        print("Reloading styles...")

        app = QApplication.instance()

        # Clear old styles
        app.setStyleSheet("")
        self.setStyleSheet("")
        QApplication.processEvents()

        # Reload fresh QSS file
        theme_name = self.theme_picker.currentText().lower()
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
            print(f"Reloading QSS from: {qss_path}")

            if os.path.exists(qss_path):
                try:
                    with open(qss_path, "r") as f:
                        qss = f.read()
                    # Apply new QSS
                    app.setStyleSheet(qss)
                    self.setStyleSheet(qss)
                    # ✅ Force the window and children to repolish
                    self.style().polish(self)
                    self.update()
                    self.repaint()
                    app.processEvents()
                    print("✅ Styles reloaded and reapplied to app.")
                except Exception as e:
                    print(f"! Error reloading StyleSheet: {e}")
            else:
                print(f"! Warning: Theme file not found: {qss_path}")

        app.processEvents()
        QMessageBox.information(self, "Reloaded", f"✅ Reloaded {theme_name.capitalize()} theme from file!")


    def init_git(self):
        try:
            self.repo = Repo(self.project_path)
            self.status.setText(f"Git repository detected at: {self.project_path}")
            self.update_log()
        except (InvalidGitRepositoryError, NoSuchPathError):
            self.repo = None
            self.status.setText("No Git repository found. Please run setup.")

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
        QMessageBox.information(self, "Setup Complete", "✅ Git + LFS Initialized!")

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
            self.status.setText("Committed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Commit Failed", str(e))

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
            self.status.setText("Returned to latest version.")
        except Exception as e:
            QMessageBox.critical(self, "Checkout Failed", str(e))

if __name__ == "__main__":
    app = QApplication([])
    window = DAWGitGUI()
    window.show()
    app.exec()

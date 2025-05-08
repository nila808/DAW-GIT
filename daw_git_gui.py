#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QComboBox
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from git import Repo, InvalidGitRepositoryError, NoSuchPathError

# --- Developer Mode Switch ---
DEVELOPER_MODE = True  # Set to False when building final app

# --- Force Correct Working Directory ---
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
elif '__file__' in globals():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- Path Helper ---
def resource_path(relative_path):
    """Get absolute path to resource"""
    if getattr(sys, '_MEIPASS', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.getcwd(), relative_path)

class DAWGitGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = None
        self.project_path = os.getcwd()

        self.setWindowTitle("DAW Git Version Control")
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.resize(1200, 700)   # width, height
        self.move(300, 200)      # x, y screen position

        main_layout = QVBoxLayout()

        # --- Logo ---
        # --- Logo Label ---
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap(resource_path("icon.png")).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio))

        # --- Logo Layout ---
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()  # Push everything to the right
        logo_layout.addWidget(self.logo_label)

        main_layout.addLayout(logo_layout)


        # --- Theme Settings ---
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout()

        self.theme_label = QLabel("Select Theme:")
        theme_layout.addWidget(self.theme_label)

        self.theme_picker = QComboBox()
        self.theme_picker.addItems(["Dark", "Light", "Funky"])
        self.theme_picker.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_picker)

        # Reload Style BTN
        self.reload_style_button = QPushButton("Reload Style")
        self.reload_style_button.clicked.connect(self.reload_styles)
        self.reload_style_button.setObjectName("reloadButton")
        theme_layout.addWidget(self.reload_style_button)
        

        theme_group.setLayout(theme_layout)
        main_layout.addWidget(theme_group)

        # --- Project Setup ---
        setup_group = QGroupBox("Project Setup")
        setup_layout = QVBoxLayout()

        # Setup BTN
        self.setup_button = QPushButton("Setup Project")
        self.setup_button.clicked.connect(self.run_setup_wizard)
        self.setup_button.setObjectName("setupButton")
        setup_layout.addWidget(self.setup_button)

        self.remote_checkbox = QCheckBox("Enable remote push (cloud sync)")
        setup_layout.addWidget(self.remote_checkbox)

        setup_group.setLayout(setup_layout)
        main_layout.addWidget(setup_group)

        # --- Status Label ---
        self.status = QLabel("Initializing...")
        main_layout.addWidget(self.status)

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

        # Commit BTN
        self.commit_button = QPushButton("Commit Changes")
        self.commit_button.clicked.connect(self.commit_changes)
        self.commit_button.setObjectName("commitButton")
        commit_layout.addWidget(self.commit_button)

        # View Unstaged Changes BTN
        self.view_changes_button = QPushButton("View Unstaged Changes")
        self.view_changes_button.clicked.connect(self.view_changes)
        commit_layout.addWidget(self.view_changes_button)
        # your_button.setObjectName("yourButtonName")

        # View Staged Change BTN
        self.view_staged_changes_button = QPushButton("View Staged Changes")
        self.view_staged_changes_button.clicked.connect(self.view_staged_changes)
        commit_layout.addWidget(self.view_staged_changes_button)
        # your_button.setObjectName("yourButtonName")

        commit_group.setLayout(commit_layout)
        main_layout.addWidget(commit_group)

        # --- Commit History Section ---
        history_group = QGroupBox("Commit History")
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Tag", "Commit ID", "Message"])
        history_layout.addWidget(self.history_table)

        buttons_layout = QHBoxLayout()

        # Checkout Selected Version BTN
        self.checkout_button = QPushButton("Checkout Selected Version")
        self.checkout_button.clicked.connect(self.checkout_selected_commit)
        buttons_layout.addWidget(self.checkout_button)
        # your_button.setObjectName("yourButtonName")

        # Return to Latest Version BTN
        self.return_latest_button = QPushButton("Return to Latest Version")
        self.return_latest_button.clicked.connect(self.return_to_latest)
        buttons_layout.addWidget(self.return_latest_button)
        # your_button.setObjectName("yourButtonName")

        history_layout.addLayout(buttons_layout)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)

        # --- Finish Layout ---
        self.setLayout(main_layout)

        # --- Theme + Git Init ---
        self.apply_theme("Dark")
        self.init_git()

        # --- Force app to quit cleanly ---
        self.destroyed.connect(QApplication.instance().quit)


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
            if DEVELOPER_MODE:
                base_path = os.path.join(os.path.dirname(__file__), 'styles')
            else:
                base_path = resource_path('styles')

            qss_path = os.path.join(base_path, theme_file)
            print(f"Loading QSS from: {qss_path}")

            if os.path.exists(qss_path):
                try:
                    with open(qss_path, "r") as f:
                        qss = f.read()
                    app = QApplication.instance()
                    app.setStyleSheet(qss)
                    self.setStyleSheet(qss)
                    print("✅ Stylesheet applied.")
                except Exception as e:
                    print(f"❗ Error applying stylesheet: {e}")
            else:
                print(f"❗ Theme file not found: {qss_path}")


    def change_theme(self, text):
        self.apply_theme(text)

    def reload_styles(self):
        print("🔄 Reloading styles...")
        app = QApplication.instance()

        # Clear all styles first
        app.setStyleSheet("")
        self.setStyleSheet("")

        # Re-apply from updated external file
        self.apply_theme(self.theme_picker.currentText())

        self.update()
        self.repaint()
        QApplication.processEvents()

        QMessageBox.information(self, "Reloaded", "✅ Styles reloaded successfully!")



    # --- Git Functions ---
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
        QMessageBox.information(self, "Setup Complete", "Git + LFS Initialized!")

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

# --- Proper App Exit ---
signal.signal(signal.SIGINT, signal.SIG_DFL)

# --- Run App ---
if __name__ == "__main__":
    app = QApplication([])
    window = DAWGitGUI()
    window.show()
    app.exec()

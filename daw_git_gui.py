from ui_strings import SNAPSHOT_MODE_UNKNOWN
#!/usr/bin/env python3

# --- Standard Library ---
import os
import sys
import re
import fnmatch
import json
import signal
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
import traceback

# --- App Modules ---
from gui_layout import build_main_ui
from daw_git_core import GitProjectManager
from daw_git_core import sanitize_git_input
from ui_strings import (
    # === General Status & Info ===
    STATUS_READY,
    STATUS_UNKNOWN,
    STATUS_BRANCH_TAKE, 
    HEADS_UP_MSG,
    HEADS_UP_TITLE,
    SESSION_SETUP_FAILED_MSG,
    PROJECT_RESTORED_MSG,
    TRACKING_NONE,
    CURRENT_BRANCH_UNKNOWN,
    CURRENT_COMMIT_UNKNOWN,
    INVALID_REPO_MSG,
    GIT_NOT_INITIALIZED_MSG,
    ALREADY_ON_COMMIT_TITLE,
    ALREADY_ON_COMMIT_MESSAGE,

    # === Snapshot View / State ===
    SNAPSHOT_INFO_TITLE,
    SNAPSHOT_INFO_MSG,
    SNAPSHOT_ALREADY_VIEWING_TITLE,
    SNAPSHOT_ALREADY_VIEWING_MSG,
    SNAPSHOT_EDIT_BLOCK_TOOLTIP,
    SNAPSHOT_EDIT_UNKNOWN,
    SNAPSHOT_MODE_UNKNOWN,
    SNAPSHOT_NO_VERSION_LINE,
    SNAPSHOT_READONLY_TOOLTIP,
    SNAPSHOT_HISTORY_LOADING,
    SNAPSHOT_HISTORY_LOADED,
    SNAPSHOT_LOAD_SUCCESS,
    SNAPSHOT_LOAD_FAILED,
    SNAPSHOT_SAVED_AUTODISABLED,
    SNAPSHOT_SAVED_WAITING,
    SNAPSHOT_SAVED_WAITING_TOOLTIP,
    SNAPSHOT_CONFIRMATION_TITLE,
    SNAPSHOT_CONFIRMATION_MSG,
    SNAPSHOT_DETACHED_WARNING,
    DELETE_SNAPSHOT_TITLE,
    DELETE_SNAPSHOT_MSG,

    # === Commit / Snapshot Status ===
    COMMIT_SUCCESS_TITLE,
    COMMIT_SUCCESS_MSG,
    CURRENT_COMMIT_TITLE,
    COMMIT_INFO_EMPTY,
    COMMIT_INFO_TITLE,
    COMMIT_REQUIRED_MSG,

    # === Snapshot Selection & Errors ===
    NO_SELECTION_TITLE,
    NO_SELECTION_MSG,
    NO_SNAPSHOT_SELECTED_TITLE,
    NO_SNAPSHOT_SELECTED_MSG,
    NO_VERSION_SELECTED_MSG,
    COMMIT_NOT_FOUND_TITLE,
    COMMIT_NOT_FOUND_MSG,

    # === Repo Errors ===
    NO_REPO_TITLE,
    NO_REPO_MSG,
    NO_REPO_COMMIT_TITLE,
    NO_REPO_COMMIT_MSG,
    NO_REPO_SAVE_MSG,
    NO_REPO_STATUS_LABEL,

    # === Commit Errors ===
    DELETE_FAILED_TITLE,
    DELETE_FAILED_MSG,
    CANT_DELETE_ROOT_TITLE,
    CANT_DELETE_ROOT_MSG,
    COULDNT_SWITCH_TITLE,
    COULDNT_SWITCH_MSG,
    CHECKOUT_FAILED_TITLE,
    CHECKOUT_FAILED_MSG,
    REBASE_FAILED_TITLE,
    REBASE_FAILED_MSG,
    UNEXPECTED_ERROR_TITLE,
    UNEXPECTED_ERROR_MSG,
    UNEXPECTED_ISSUE_TITLE,
    UNEXPECTED_ISSUE_MSG,
    CROSS_BRANCH_COMMIT_MSG,

    # === Branching ===
    ALREADY_ON_BRANCH_TITLE,
    ALREADY_ON_BRANCH_MSG,
    DETACHED_HEAD_LABEL,
    DETACHED_HEAD_TITLE,
    DETACHED_HEAD_MSG,
    DETACHED_HEAD_LABEL,
    SESSION_BRANCH_LABEL,
    ROLE_LABEL_MAP,
    BRANCH_NO_SELECTION,

    # === Backup ===
    BACKUP_RESTORED_TITLE,
    BACKUP_RESTORED_MSG,
    NO_BACKUP_FOUND_TITLE,
    NO_BACKUP_FOUND_MSG,

    # === Remote ===
    REMOTE_ADDED_TITLE,
    REMOTE_ADDED_MSG,
    REMOTE_SETUP_FAILED_TITLE,
    REMOTE_SETUP_FAILED_MSG,

    # === Warnings & Safety ===
    UNSAVED_CHANGES_TITLE,
    UNSAVED_CHANGES_MSG,
    UNSAVED_CHANGES_WARNING,
    UNSAFE_DIRTY_EDITS_TITLE,
    UNSAFE_DIRTY_EDITS_MSG,
    DIRTY_EDIT_WARNING,

    # === Return to Latest ===
    RETURN_TO_LATEST_TITLE,
    RETURN_TO_LATEST_MSG,
    TOOLTIP_RETURN_TO_LATEST,

    # === UI Labels & Buttons ===
    COMMIT_CHANGES_BTN,
    CONNECT_REMOTE_BTN,
    START_NEW_VERSION_BTN,
    TAG_SNAPSHOT_BTN,
    RETURN_TO_LATEST_BTN,
    BTN_TAG_MAIN_MIX,
    BTN_TAG_CREATIVE_TAKE,
    BTN_TAG_ALT_MIX,
    BTN_TAG_CUSTOM_LABEL,
    BTN_LAUNCH_DAW_FILE,
    BTN_OPEN_VERSION_IN_DAW,
    BTN_OPEN_COMMIT_PANEL,
    BTN_MAIN_MIX,
    BTN_CREATIVE_TAKE,
    BTN_ALT_MIX,
    BTN_LOAD_SNAPSHOT,
    BTN_WHERE_AM_I,
    BTN_QUICK_SAVE, 
    SNAPSHOT_MODE_UNKNOWN,
    SNAPSHOT_EDITABLE_TOOLTIP, 
    STATUS_SESSION_LABEL, 
    SNAPSHOT_SWITCH_WARNING_TITLE,
    SNAPSHOT_SWITCH_WARNING_MSG,

    # === Role tags ===
    ROLE_KEY_MAIN_MIX,
    ROLE_KEY_CREATIVE_TAKE,
    ROLE_KEY_ALT_MIXDOWN,
    ROLE_KEY_CUSTOM, 
    CONFIRM_REPLACE_MAIN_TITLE,
    CONFIRM_REPLACE_MAIN_MSG, 
    STATUS_TAGGED_AS_MAIN_MIX, 
    INVALID_LABEL_TITLE, 
    INVALID_LABEL_MSG, 
    CREATE_VERSION_LINE_TITLE,
    CREATE_VERSION_LINE_MSG, 
    ABLETON_MAY_BE_OPEN_TITLE,
    ABLETON_MAY_BE_OPEN_MSG


)


# --- Git ---
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from git.exc import GitCommandError

# --- PyQt6 ---
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, 
    QTableWidgetItem, QInputDialog, QAbstractItemView, 
    QTableWidget
)
from PyQt6.QtCore import Qt, QSettings, QTimer, pyqtSlot


class NumericItem(QTableWidgetItem):
    def __init__(self, number, text=None):
        super().__init__(f"#{number}" if text is None else text)
        self.number = number

    def __lt__(self, other):
        if isinstance(other, NumericItem):
            return self.number < other.number
        return super().__lt__(other)
    
# from PyQt6.QtWidgets import 

# --- App Bootstrap ---
if QApplication.instance() is None:
    _app = QApplication(sys.argv)

# --- Developer Configuration ---
DEVELOPER_MODE = True

def qt_exception_hook(exctype, value, traceback):
    print(f"[CRITICAL] Uncaught Qt exception:", value)

sys.excepthook = qt_exception_hook


class DAWGitApp(QMainWindow): 
    
    def __init__(self, project_path=None, build_ui=True):
        super().__init__()

        self.settings_path = Path.home() / ".dawgit_settings"
        self.repo = None
        self.current_commit_id = None
        self.settings = QSettings("DAWGitApp", "DAWGit")
        # 🧪 Test mode: auto-close all modals safely
        if os.getenv("DAWGIT_TEST_MODE") == "1":
            from PyQt6.QtWidgets import QMessageBox, QInputDialog

            QMessageBox.question = lambda *a, **kw: QMessageBox.StandardButton.Yes
            QMessageBox.information = lambda *a, **kw: None
            QMessageBox.warning = lambda *a, **kw: None
            QMessageBox.critical = lambda *a, **kw: None

            # if os.getenv("DAWGIT_FORCE_INPUT") == "1":
            #     QInputDialog.getText = lambda *a, **k: ("test_input", True)
            # QInputDialog.getItem = lambda *a, **kw: ("main", True)

            # Input dialogs should be patched directly in tests
            pass

        self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]

        # ✅ Set project path before loading anything project-specific
        if project_path is not None:
            self.project_path = Path(project_path)
        elif os.environ.get("DAWGIT_FORCE_TEST_PATH"):
            self.project_path = Path(os.environ["DAWGIT_FORCE_TEST_PATH"])
            print(f"[TEST MODE] Forced project path via env var: {self.project_path}")
        else:
            self.project_path = None

        # ✅ Load metadata and roles
        self.load_project_marker()
        self.commit_roles = {}
        self.load_commit_roles()

        # ✅ Build the UI
        if build_ui:
            self.setup_ui()

        # 🔁 Auto-restore project ONLY if one wasn't already set
        if self.project_path is None:
            last_path = self.load_saved_project_path()
            if last_path and Path(last_path).is_dir() and (Path(last_path) / ".git").exists():
                print(f"🔁 Restoring last project: {last_path}")
                self.load_project_folder(last_path)
            else:
                print("⚠️ Last project path invalid or no .git folder.")

        # ✅ Apply custom stylesheet (QSS)
        try:
            with open("styles/dawgit_styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"[WARNING] Stylesheet not loaded: {e}")

        # ✅ Show the welcome modal if no project path is set (First-time launch scenario)
        if self.project_path is None:
            self.maybe_show_welcome_modal()  # This should trigger the modal when no path is set

        # 1. Load saved path if not already set
        if self.project_path is None:
            last_path = self.load_saved_project_path()
            if last_path:
                self.project_path = Path(last_path)

        # 2. Change directory and initialize Git
        if self.project_path and self.project_path.exists():
            os.chdir(self.project_path)
            print(f"[DEBUG] Loaded project path: {self.project_path}")
            self.init_git()

            # ✅ Load roles only *after* init_git
            if self.repo:
                self.load_commit_roles()

                if self.repo.head.is_detached:
                    print("[DEBUG] Repo is in detached HEAD state")
                    self._show_warning(
                        "🎛️ You're browsing a past version of your session.\n\n"
                        "Feel free to explore—but to lay down a new take, you'll need to start a fresh version line."
                    )

                if hasattr(self, "project_label"):
                    self.project_label.setText(f"🎵 Tracking Project: {self.project_path.name}")
                if hasattr(self, "status_label"):
                    self.snapshot_page.status_label.setText(PROJECT_RESTORED_MSG)
                if build_ui and hasattr(self, "history_table"):
                    self.load_commit_history()
            else:
                if hasattr(self, "project_label"):
                    self.project_label.setText(SNAPSHOT_LOAD_FAILED)
                if hasattr(self, "status_label"):
                    self.snapshot_page.status_label.setText(INVALID_REPO_MSG)

        elif build_ui:
            folder = QFileDialog.getExistingDirectory(self, "🎵 Select Your DAW Project Folder")
            if folder:
                selected_path = Path(folder)
                if not self.is_valid_daw_folder(selected_path):
                    QMessageBox.warning(
                        self,
                        "Invalid Folder",
                        "❌ That folder doesn't contain an Ableton (.als) or Logic (.logicx) file.\n\nPlease select a valid DAW project."
                    )
                    return
                self.project_path = selected_path
                os.chdir(self.project_path)
                print(f"[DEBUG] User selected valid DAW project: {self.project_path}")
                self.save_last_project_path()
                self.init_git()

                if self.repo:
                    self.load_commit_roles()

                    if self.repo.head.is_detached:
                        print("[DEBUG] Repo is in detached HEAD state (user-selected project)")
                        self._show_warning(
                            "🎛️ You're browsing a past version of your session.\n\n"
                            "To drop a new mixdown or version, start a new version line first."
                        )

                    if hasattr(self, "project_label"):
                        self.project_label.setText(f"🎵 Tracking Project: {self.project_path.name}")
                    if hasattr(self, "status_label"):
                        self.snapshot_page.status_label.setText(NEW_PROJECT_SELECTED_MSG)
                    if hasattr(self, "history_table"):
                        self.load_commit_history()
                else:
                    if hasattr(self, "project_label"):
                        self.project_label.setText(SNAPSHOT_LOAD_FAILED)
                    if hasattr(self, "status_label"):
                        self.snapshot_page.status_label.setText(INVALID_REPO_MSG)
            else:
                QMessageBox.information(
                    self,
                    "No Project Selected",
                    "🎛️ No project folder selected. Click 'Setup Project' to start tracking your music session."
                )
                if hasattr(self, "project_label"):
                    self.project_label.setText(TRACKING_NONE)
                if hasattr(self, "status_label"):
                    self.snapshot_page.status_label.setText(STATUS_READY)

        # ✅ Final UI sync safety net
        if hasattr(self, "status_label"):
            self.update_status_label()


    def setup_ui(self):
        build_main_ui(self)

    # def pretty_role(self, role_key):
    #     return {
    #         "main_mix": ROLE_KEY_MAIN_MIX,
    #         "creative_take": ROLE_KEY_CREATIVE_TAKE,
    #         "alt_mixdown": ROLE_KEY_ALT_MIXDOWN,
    #         "test_custom_tag": ROLE_KEY_CUSTOM
    #     }.get(role_key, role_key.replace("_", " ").title() if role_key else "")

    def pretty_role(self, role_key):
        return ROLE_LABEL_MAP.get(role_key, role_key.replace("_", " ").title() if role_key else "")

    

    def maybe_show_welcome_modal(self):
        print("[DEBUG] Entering maybe_show_welcome_modal()")  # Debug entry point

        # Show the modal only if no project path is set
        if not self.project_path:
            print("[DEBUG] No project path set, showing modal...")

            choice = QMessageBox.warning(
                self,
                "🎉 Welcome to DAW Git",
                "No project folder selected. Would you like to open a project now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if choice == QMessageBox.StandardButton.Yes:
                print("[DEBUG] User chose 'Yes'")
                selected = QFileDialog.getExistingDirectory(self, "Select Your Project Folder")
                print(f"[DEBUG] User selected folder: {selected}")
                if selected:
                    self.project_path = Path(selected)
                    self.init_git()
                    self.load_commit_history()
                    return
                else:
                    print("[DEBUG] No folder selected, exiting setup.")
                    self.close()
            elif choice == QMessageBox.StandardButton.No:
                print("[DEBUG] User chose 'No'")
                self.close()
                self.project_path = None
                self.clear_last_project_path()
                print("[DEBUG] Last path reset after 'No' selected.")

            # ✅ Only access snapshot_page if it exists
            if hasattr(self, "snapshot_page"):
                self.snapshot_page.status_label.setText(NO_REPO_MSG)
                self.status_label = self.snapshot_page.status_label
                self.update()
            return

        # After "No" selected or if path is invalid
        print("[DEBUG] Skipping last path loading and repo setup after 'No' selected.")
        self.clear_last_project_path()
        self.project_path = None
        if hasattr(self, "snapshot_page"):
            self.snapshot_page.status_label.setText(NO_REPO_MSG)
            self.update()
        return

        # After "No" was selected, skip all path loading and repo initialization:
        print("[DEBUG] Skipping last path loading and repo setup after 'No' selected.")  # Debug message confirming skipping
        
        # **Explicitly clear settings and last path**
        self.clear_last_project_path()  # Ensure settings don't hold the last invalid path
        self.project_path = None  # Explicitly clear the project path to prevent any further operations

        # Update status label to reflect no repo loaded
        self.snapshot_page.status_label.setText(NO_REPO_MSG) # Set the status label text
        self.update()  # Force the UI to refresh and update with new status
        return  # End method flow after "No"


    def run_backup(self):
        if not self.project_path:
            print("[WARN] Cannot run backup — project path is not set.")
            return

        backup_dir = self.project_path / "Backup"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_files = []

        # Backup DAW files
        for ext in ("*.als", "*.logicx"):
            for file in self.project_path.glob(ext):
                backup_name = f"{file.stem} [{timestamp}]{file.suffix}"
                dest = backup_dir / backup_name
                shutil.copy2(file, dest)
                backup_files.append(str(dest.relative_to(self.project_path)))

        # Backup role data
        roles_file = self.project_path / ".dawgit_roles.json"
        if roles_file.exists():
            dest = backup_dir / f"dawgit_roles_backup_{timestamp}.json"
            shutil.copy2(roles_file, dest)
            backup_files.append(str(dest.relative_to(self.project_path)))

        print(f"[DEBUG] Backed up: {backup_files}")

        # ✅ Update PROJECT_MARKER.json
        if hasattr(self, "project_marker"):
            self.project_marker.setdefault("backup_info", {})["last_backup_time"] = datetime.now().isoformat()
            self.project_marker["backup_info"]["backup_files"] = backup_files
            self.save_project_marker()
            

    def load_project_marker(self):
        """
        Loads PROJECT_MARKER.json into self.project_marker if it exists.
        Initializes it as an empty dict otherwise.
        """
        if not hasattr(self, "project_path") or not self.project_path:
            print("[DEBUG] Skipping project marker load — project_path not set")
            self.project_marker = {}
            return

        marker_path = Path(self.project_path) / "PROJECT_MARKER.json"
        if marker_path.exists():
            try:
                with open(marker_path, "r") as f:
                    self.project_marker = json.load(f)
                    print(f"[DEBUG] Loaded PROJECT_MARKER.json from {marker_path}")
            except Exception as e:
                print(f"[ERROR] Failed to load PROJECT_MARKER.json: {e}")
                self.project_marker = {}
        else:
            self.project_marker = {}
            print("[DEBUG] No PROJECT_MARKER.json found — using defaults")


    def handle_auto_save_toggle(self, state):
        if state == Qt.CheckState.Checked.value:
            self.status_message("✅ Auto-save enabled — will commit automatically")
        else:
            self.status_message("⏸️ Auto-save disabled")
            

    def save_project_marker(self):
        """
        Saves the current self.project_marker state to PROJECT_MARKER.json.
        """
        if not hasattr(self, "project_path") or not self.project_path:
            print("[DEBUG] Skipping project marker save — project_path not set")
            return

        marker_path = Path(self.project_path) / "PROJECT_MARKER.json"
        try:
            with open(marker_path, "w") as f:
                json.dump(self.project_marker, f, indent=2)
                print(f"[DEBUG] Saved PROJECT_MARKER.json to {marker_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save PROJECT_MARKER.json: {e}")


    def change_project_folder(self):
        # Let user select a new DAW project folder
        folder = QFileDialog.getExistingDirectory(self, "Select DAW Project Folder")
        if folder:
            new_path = Path(folder)
            if not self.is_valid_daw_folder(new_path):
                QMessageBox.warning(
                    self,
                    "Invalid Folder",
                    "❌ That folder doesn't contain an Ableton (.als) or Logic (.logicx) file.\n\nPlease select a valid DAW project."
                )
                return
            self.project_path = new_path
            os.chdir(self.project_path)
            self.save_last_project_path()
            self.init_git()
            self.load_commit_history()
            self.update_project_label()
            self.status_message(f"🎵 Changed project folder to: {self.project_path}")


    def clear_last_project_path(self):
        """
        Clears the last saved project path in the settings.
        This method explicitly sets the `last_project_path` to an empty string
        and forces the settings to sync immediately.
        """
        # Initialize QSettings
        settings = QSettings("DAWGitApp", "DAWGit")

        # Debug: Print the current value of 'last_project_path' before clearing
        print(f"[DEBUG] Current last_project_path: {settings.value('last_project_path')}")

        # Set the last_project_path to an empty string
        settings.setValue("last_project_path", "")

        # Reset internal project path and repo
        self.project_path = None
        self.repo = None

        # Use a separate flag for unsaved changes
        self.unsaved_changes_flag = False  # Clear the unsaved changes flag

        self.update_status_label()  # Update status label

        # Sync the settings to ensure the change is immediately written to disk
        settings.sync()  # Ensures that the change is saved immediately

        # Debug: Confirm that the last project path has been cleared
        print("[DEBUG] Cleared last project path in settings.")


    def show_branch_selector(self):
        if not self.repo:
            QMessageBox.warning(self, NO_REPO_TITLE, NO_REPO_MSG)
            return

        branches = [head.name for head in self.repo.heads]
        current_branch = self.repo.active_branch.name if not self.repo.head.is_detached else None

        selected, ok = QInputDialog.getItem(
            self,
            "🎹 Select a Version Line",
            "Choose another version line to load:",
            branches,
            editable=False
        )
        if ok and selected and selected != current_branch:
            self.checkout_branch(selected)


    def load_snapshot_clicked(self):
        selected_row = self.snapshot_page.commit_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, NO_SNAPSHOT_SELECTED_TITLE, NO_SNAPSHOT_SELECTED_MSG)
            return
        self.checkout_selected_commit()


    def clean_blocking_files(self, filenames={".DS_Store"}):
        """
        Removes known untracked blocking files (e.g., .DS_Store) before checkout.
        """
        if not self.repo:
            return

        untracked = self.repo.untracked_files
        for file in untracked:
            if Path(file).name in filenames:
                try:
                    full_path = self.project_path / file
                    os.remove(full_path)
                    print(f"[DEBUG] Removed blocking file: {full_path}")
                except Exception as e:
                    print(f"[WARNING] Could not remove {file}: {e}")


    def checkout_branch(self, branch_name):
        """
        Switch to a different branch/version line safely.
        """
        if not self.repo:
            self.snapshot_page.status_label.setText(GIT_NOT_INITIALIZED_MSG)
            return

        if branch_name not in [h.name for h in self.repo.heads]:
            self.snapshot_page.status_label.setText(f"⚠️ Branch '{branch_name}' not found.")
            return

        try:
            self.clean_blocking_files()

            # 🛡️ Save backup before switching
            self.stash_uncommitted_changes("Switching branches")
            
            # 🔀 Perform checkout
            self.repo.git.checkout(branch_name)
            self.update_log()
            self.update_project_label()
            self.update_status_label()
            self.set_commit_id_from_head()
            self.update_role_buttons()
            # self.update_branch_dropdown()

            self.update_session_branch_display()
            self.update_version_line_label()

            self.snapshot_page.status_label.setText(f"✅ Switched to branch '{branch_name}'")
        except Exception as e:
            error_msg = f"Couldn't switch versions:\n\n{e}"
            self._show_error(error_msg)
            self.snapshot_page.status_label.setText(f"❌ {error_msg}")
            print(f"[ERROR] Branch switch failed: {e}")


    def stash_uncommitted_changes(self, message="DAWGit auto-stash"):
        result = self.git.stash_uncommitted_changes(message)
        if result["status"] == "stashed":
            print(f"[DEBUG] Changes stashed: {message}")
        elif result["status"] == "clean":
            print("[DEBUG] No changes to stash.")
        else:
            print(f"[WARN] Failed to stash changes: {result.get('message')}")


    def get_tag_for_commit(self, commit_sha):
        """Returns the first tag associated with a given commit hash."""
        try:
            # Run the git command to get tags associated with the given commit
            result = subprocess.run(
                ["git", "tag", "--points-at", commit_sha],  # Git command to get the tag
                cwd=self.project_path,  # Set the working directory to the project path
                env=self.custom_env(),  # Set the environment variables (custom_env() is assumed to be defined elsewhere)
                capture_output=True,  # Capture both stdout and stderr from the git command
                text=True  # Ensure the output is returned as a string
            )
            
            # Strip any leading/trailing whitespace and split by lines to get the tags
            tags = result.stdout.strip().splitlines()
            
            # Return the first tag if found, otherwise return an empty string
            return tags[0] if tags else ""
        
        except Exception as e:
            # In case of an error, print the error and return an empty string
            print(f"[ERROR] get_tag_for_commit failed for {commit_sha}: {e}")
            return ""


    def init_git(self):
        print("[DEBUG] Calling GitProjectManager.init_repo()")

        self.git = GitProjectManager(self.project_path)
        result = self.git.init_repo()

        if result["status"] == "ok":
            self.repo = self.git.repo
            self.save_last_project_path()
            self.load_commit_roles()

            if hasattr(self, "update_status_label"):
                self.update_status_label()

            if hasattr(self, "history_table") and self.repo.head.is_valid():
                self.current_commit_id = self.repo.head.commit.hexsha
                self.load_commit_history()

            self.update_session_status_mode() 

        elif result["status"] == "detached":
            self.repo = self.git.repo  # still bind the repo to self
            if hasattr(self, "status_label"):
                self.snapshot_page.status_label.setText(DETACHED_HEAD_LABEL)
            if hasattr(self, "detached_warning_label"):
                self.detached_warning_label.setText(
                    "🧭 You’re viewing a snapshot — to save changes, return to latest or start a new version line."
                )
                self.detached_warning_label.show()

        else:
            self.repo = None
            print(f"[ERROR] init_git(): {result['message']}")

        self.update_session_labels()
        return {"status": "ok", "message": "Repo initialized."}

    




    def bind_repo(self, path=None):
        """
        Safely rebind the repo object, update commit ID and refresh UI state.
        """
        try:
            repo_path = Path(path or self.project_path)
            self.repo = Repo(repo_path)
            self.load_commit_roles()

            if self.repo.head.is_valid():
                self.current_commit_id = self.repo.head.commit.hexsha
                print(f"[DEBUG] Repo rebound: HEAD = {self.current_commit_id[:7]}")
            else:
                self.current_commit_id = None
                print("[DEBUG] HEAD not valid or detached")

            # ✅ Only refresh history UI if table exists
            if hasattr(self, "history_table"):
                self.load_commit_history()

            if hasattr(self, "update_status_label"):
                self.update_status_label()

            if hasattr(self, "update_role_buttons"):
                self.update_role_buttons()

            # ✅ NEW: Update commit button state based on safe/unsafe mode
            if hasattr(self.commit_page, "update_snapshot_editing_state"):
                self.commit_page.update_snapshot_editing_state()

            if hasattr(self, "commit_page"):
                is_detached = self.repo.head.is_detached
                in_editable = ".dawgit_checkout_work" in str(self.project_path)

                if is_detached and not in_editable:
                    # 🧠 Disable commit panel if editing not allowed
                    if hasattr(self.commit_page, "set_commit_controls_enabled"):
                        is_detached = self.repo.head.is_detached
                        in_editable = ".dawgit_checkout_work" in str(self.project_path)
                        tooltip = ""
                        if is_detached and not in_editable:
                            tooltip = SNAPSHOT_EDIT_BLOCK_TOOLTIP
                            self.commit_page.set_commit_controls_enabled(False, tooltip)
                        else:
                            self.commit_page.set_commit_controls_enabled(True, "")
                else:
                    self.commit_page.set_commit_controls_enabled(True, "")

        except Exception as e:
            print(f"[ERROR] Failed to bind repo: {e}")
            import traceback
            traceback.print_exc()

            # Only clear if repo is truly broken — not on UI errors
            if not self.repo or not hasattr(self.repo, "head"):
                self.repo = None
                self.current_commit_id = None

    @property
    def branch_dropdown(self):
        if hasattr(self, "branch_page"):
            return self.branch_page.branch_dropdown
        return None


    def update_snapshot_mode_label(self):
        if not self.repo:
            self.snapshot_mode_label.setText(SNAPSHOT_NO_VERSION_LINE)
            return

        if self.repo.head.is_detached:
            self.snapshot_mode_label.setText(SNAPSHOT_UNKNOWN_STATE)

        else:
            try:
                branch = self.repo.active_branch.name
                sha = self.repo.head.commit.hexsha[:7]
                self.snapshot_mode_label.setText(f"🎧 Editing: {sha} on {branch}")
            except Exception:
                self.snapshot_mode_label.setText(SNAPSHOT_EDIT_UNKNOWN)


    def update_session_status_mode(self):
        """Updates the persistent session mode label based on HEAD state."""
        if not hasattr(self, "status_mode_label") or not self.repo:
            return

        is_detached = self.repo.head.is_detached
        in_editable = ".dawgit_checkout_work" in str(self.project_path)

        if is_detached and not in_editable:
            self.status_mode_label.setText(SNAPSHOT_READONLY_TOOLTIP)
            self.status_mode_label.setToolTip(SNAPSHOT_EDIT_BLOCK_TOOLTIP)
        else:
            branch = self.repo.active_branch.name if not is_detached else "detached"
            self.status_mode_label.setText(f"🎚️ Editing: version on '{branch}'")
            self.status_mode_label.setToolTip(SNAPSHOT_EDITABLE_TOOLTIP)


    def update_branch_dropdown(self):
        self.branch_dropdown.blockSignals(True)
        self.branch_dropdown.clear()

        branches = [head.name for head in self.repo.heads]
        self.branch_dropdown.addItems(branches)

        try:
            active_branch = self.repo.active_branch.name
            if active_branch in branches:
                index = branches.index(active_branch)
                self.branch_dropdown.setCurrentIndex(index)
        except TypeError:
            # Handle detached HEAD
            self.branch_dropdown.setCurrentText("Detached HEAD")

        self.branch_dropdown.blockSignals(False)


    def open_in_daw(self):
        """🎧 Launch the current snapshot in the DAW (uses editable copy if available)."""
        try:
            editable_dir = Path(self.project_path) / ".dawgit_checkout_work"
            editable_als = next(editable_dir.glob("*_editable.als"), None)

            if editable_als and editable_als.exists():
                subprocess.run(["open", str(editable_als)])
                print(f"[DEBUG] Opened editable copy in DAW: {editable_als}")
            elif self.current_daw_file and Path(self.current_daw_file).exists():
                subprocess.run(["open", str(self.current_daw_file)])
                print(f"[DEBUG] Opened original DAW file: {self.current_daw_file}")
            else:
                QMessageBox.warning(
                    self,
                    "No DAW File Found",
                    "❌ Could not locate a valid DAW project file to open."
                )
        except Exception as e:
            QMessageBox.critical(self, LAUNCH_FAILED_TITLE, LAUNCH_FAILED_MSG.format(error=e))


    def get_relevant_dirty_files(self):
        """Returns a list of user-relevant dirty files, excluding safe noise and editable folders."""
        ignored = {
            ".DS_Store",
            "PROJECT_MARKER.json",
            ".dawgit_roles.json",
            ".dawgit_meta.json",  # optional, in case you add it
        }
        excluded_paths = [".dawgit_cache/", ".dawgit_checkout_work/"]
        excluded_keywords = ["editable", "placeholder"]

        relevant_dirty = []

        try:
            dirty_lines = self.repo.git.status("--porcelain").splitlines()
        except Exception as e:
            print(f"[WARN] Failed to read dirty status: {e}")
            return []

        for line in dirty_lines:
            path = line[3:].strip()
            name = Path(path).name

            if (
                name not in ignored
                and not any(path.startswith(p) for p in excluded_paths)
                and not any(k in name.lower() for k in excluded_keywords)
            ):
                relevant_dirty.append(path)

        return relevant_dirty


    def scroll_to_commit_sha(self, sha):
        """
        Scrolls to and selects the commit row matching the given SHA.
        Ensures the tooltip is set correctly for test verification.
        """
        for row in range(self.history_table.rowCount()):
            sha_item = self.history_table.item(row, 2)
            if sha_item and sha in sha_item.text():
                self.history_table.selectRow(row)
                self.history_table.scrollToItem(sha_item, QAbstractItemView.ScrollHint.PositionAtCenter)
                # 🩹 Patch: Set tooltip manually in case it wasn't applied during update_log
                sha_item.setToolTip(sha)
                print(f"[DEBUG] ✅ Delayed scroll and select to HEAD row {row}")
                break


    def return_to_latest_clicked(self):
        try:
            if not self.repo:
                self._show_warning("No Git repository loaded.")
                return

            # 🎯 If in detached HEAD, switch back to 'main'
            if self.repo.head.is_detached:
                print("[DEBUG] Repo is in detached HEAD. Attempting to switch to 'main'")

                relevant_dirty = []  # ✅ Always declare this early

                ignored = {
                    ".DS_Store",
                    "PROJECT_MARKER.json",
                    ".dawgit_roles.json",
                    ".dawgit_meta.json",
                }
                excluded_paths = [".dawgit_cache/", ".dawgit_checkout_work/"]
                excluded_keywords = ["editable", "placeholder"]

                dirty_lines = self.repo.git.status("--porcelain").splitlines()

                for line in dirty_lines:
                    path = line[3:].strip()
                    name = Path(path).name
                    if (
                        name not in ignored
                        and not any(path.startswith(p) for p in excluded_paths)
                        and not any(k in name.lower() for k in excluded_keywords)
                    ):
                        relevant_dirty.append(path)

                relevant_dirty = self.get_relevant_dirty_files()
                if relevant_dirty:
                    print(f"[BLOCK] Dirty files detected that are not safe to discard: {relevant_dirty}")
                    QMessageBox.warning(
                        self,
                        UNSAFE_DIRTY_EDITS_TITLE,
                        UNSAFE_DIRTY_EDITS_MSG.format(file_list="\n".join(f"• {f}" for f in relevant_dirty))
                    )
                    return

                # 🩹 PATCH: Clean tracked and untracked noise files to prevent checkout conflicts
                safe_noise_files = {
                    ".DS_Store",
                    "PROJECT_MARKER.json",
                    ".dawgit_roles.json",
                    ".dawgit_cache",  # ✅ NEW — allow StudioGit cache folder as safe
                }
                reset_tracked = []
                remove_untracked = []

                for path in self.repo.index.diff(None):
                    if Path(path.a_path).name in safe_noise_files:
                        reset_tracked.append(path.a_path)

                untracked = {Path(f).name: f for f in self.repo.untracked_files}
                for name in safe_noise_files:
                    if name in untracked:
                        full_path = self.project_path / untracked[name]
                        remove_untracked.append(str(full_path))

                if reset_tracked:
                    subprocess.run(["git", "restore", "--staged"] + reset_tracked,
                                cwd=self.project_path, env=self.custom_env(), check=True)
                    subprocess.run(["git", "checkout", "--"] + reset_tracked,
                                cwd=self.project_path, env=self.custom_env(), check=True)

                for path in remove_untracked:
                    try:
                        os.remove(path)
                        print(f"[DEBUG] Removed untracked file: {path}")
                    except Exception as e:
                        print(f"[WARNING] Could not remove {path}: {e}")

                if hasattr(self, "file_watcher"):
                    for path in remove_untracked:
                        self.file_watcher.removePath(str(path))

                # 🔍 DEBUG: List branches
                try:
                    branch_list = subprocess.run(
                        ["git", "branch", "-vv"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    print("[DEBUG] git branch -vv BEFORE SWITCH:\n", branch_list.stdout)

                    # ❗ Check if 'main' branch exists
                    branch_names = [line.strip().lstrip("* ").split()[0] for line in branch_list.stdout.splitlines()]
                    if "main" not in branch_names:
                        print("[ERROR] 'main' branch does not exist — cannot return to latest.")
                        self._show_warning("Cannot return to latest — no 'main' version line exists in this project.")
                        return

                except subprocess.CalledProcessError as e:
                    print("[ERROR] Failed to list branches before switch:", e)
                    self._show_error("❌ Failed to retrieve branch list before attempting switch.")
                    return


                # ✅ Remove editable checkout folder to prevent overwrite error
                checkout_path = self.project_path / ".dawgit_checkout_work"
                if checkout_path.exists():
                    try:
                        shutil.rmtree(checkout_path)
                        print(f"[CLEANUP] Removed editable snapshot folder: {checkout_path}")
                    except Exception as e:
                        print(f"[ERROR] Failed to remove editable folder: {e}")
                        self._show_error(f"❌ Failed to remove editable snapshot folder:\n{e}")
                        return


                # ✅ Attempt to switch to main
                try:
                    print("[DEBUG] Running: git switch main")
                    result = subprocess.run(
                        ["git", "switch", "main"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    print("[DEBUG] git switch stdout:\n", result.stdout)
                    print("[DEBUG] git switch stderr:\n", result.stderr)

                    status = subprocess.run(
                        ["git", "status"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        capture_output=True,
                        text=True,
                    )
                    print("[DEBUG] git status:\n", status.stdout)

                except subprocess.CalledProcessError as e:
                    print("[ERROR] git switch failed:", e)
                    print("STDOUT:", e.stdout)
                    print("STDERR:", e.stderr)
                    self._show_error("❌ Git switch to 'main' failed. Please check your branches.")
                    return

                self.repo = Repo(self.project_path)
                subprocess.run(["git", "lfs", "checkout"], cwd=self.project_path, env=self.custom_env(), check=True)

                self.bind_repo()

                try:
                    head_commit = self.repo.head.commit
                    self.current_commit_id = head_commit.hexsha
                except Exception as e:
                    print(f"[ERROR] Failed to get HEAD commit after switch: {e}")
                    self._show_error("❌ Failed to return to the latest commit.")
                    return

                print(f"[DEBUG] Repo rebound: HEAD = {self.current_commit_id[:7]}")
                self.load_commit_history()
                self.update_status_label()
                self.update_role_buttons()
                self.update_project_label()

                # ✅ Define editable checkout path
                editable_path = self.project_path / ".dawgit_checkout_work"
                self.editable_checkout_path = editable_path
                print(f"[INFO] Returned to latest — editable copy path: {editable_path}")

                # ✅ Update snapshot UI state
                self.update_snapshot_status_labels()

                if self.repo.head.is_detached:
                    self.branch_label.setText(
                        SESSION_BRANCH_LABEL.format(
                            branch=self.repo.active_branch.name,
                            take=self.get_current_take_name()
                        )
                    )
                else:
                    self.update_session_labels()
                    self.detached_warning_label.hide()
                    self.open_in_daw_btn.setVisible(True)

                head_sha = self.repo.head.commit.hexsha[:7]
                QTimer.singleShot(100, lambda: self.scroll_to_commit_sha(head_sha))
                selected_row = None
                for row in range(self.snapshot_page.commit_table.rowCount()):
                    item = self.snapshot_page.commit_table.item(row, 2)
                    if item and head_sha in (item.toolTip() or item.text()):
                        selected_row = row
                        break

                if selected_row is not None:
                    QTimer.singleShot(0, lambda: (
                        self.snapshot_page.commit_table.scrollToItem(
                            self.snapshot_page.commit_table.item(selected_row, 1),
                            QTableWidget.ScrollHint.PositionAtCenter),
                        self.snapshot_page.commit_table.selectRow(selected_row)
                    ))
                    print(f"[DEBUG] ✅ Delayed scroll and select to HEAD row {selected_row}")

                QMessageBox.information(self, RETURN_TO_LATEST_TITLE, RETURN_TO_LATEST_MSG.format(branch="main"))

            else:
                current_branch = self.repo.active_branch.name
                # self._show_info(f"Already on branch '{current_branch}'. No action needed.")
                QMessageBox.information(
                    self,
                    RETURN_TO_LATEST_TITLE,
                    f"🎉 You're already on the latest version line!\n\n"
                    f"Branch: {current_branch}\nCommit: {self.repo.head.commit.hexsha[:7]}"
                )
                self._set_commit_id_from_selected_row()
                self.update_status_label()
                self.update_role_buttons()
                self.update_project_label()
                self.update_session_labels()
                self.detached_warning_label.hide()
                self.open_in_daw_btn.setVisible(True)


            # 🔁 Refresh commit UI state after returning to main
            if hasattr(self.commit_page, "update_snapshot_editing_state"):
                self.commit_page.update_snapshot_editing_state()

            if hasattr(self, "commit_page"):
                is_detached = self.repo.head.is_detached
                in_editable = ".dawgit_checkout_work" in str(self.project_path)
                if is_detached and not in_editable:
                    self.commit_page.set_commit_controls_enabled(
                        False,
                        SNAPSHOT_EDIT_BLOCK_TOOLTIP
                    )
                else:
                    self.commit_page.set_commit_controls_enabled(True, "")

            self.update_session_status_mode()

        except Exception as e:
            self._show_error(f"❌ Failed to return to the latest commit:\n\n{e}")

   
    def update_session_labels(self):
        if not self.repo:
            return

        try:
            is_detached = self.repo.head.is_detached

            if is_detached:
                branch = "detached"
            else:
                branch = self.repo.active_branch.name

            # ✅ Always define this safely
            display_branch = self.normalize_branch_name(branch)

            take = self.get_current_take_name()
            label = (
                STATUS_BRANCH_TAKE.format(branch=display_branch, take=take)
                if not is_detached
                else DETACHED_HEAD_LABEL
            )

            if hasattr(self, "branch_label"):
                self.branch_label.setText(label)

        except Exception as e:
            print(f"[DEBUG] Error updating session labels: {e}")

       

    def run_setup(self):
        confirm = QMessageBox.question(
            self,
            SNAPSHOT_CONFIRMATION_TITLE,
            SNAPSHOT_CONFIRMATION_MSG,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if confirm != QMessageBox.StandardButton.Yes:
            print("🛑 Setup cancelled by user.")
            return

        print("✅ User confirmed project setup.")

        if not self.project_path or not self.project_path.exists():
            folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not folder:
                return
            self.project_path = Path(folder)

        try:
            os.chdir(self.project_path)

            # ✅ Check if already a valid Git repo with commits
            if (self.project_path / ".git").exists():
                self.bind_repo()
                if self.repo.head.is_valid():
                    print("ℹ️ Repo already initialized with commits — skipping setup.")
                    self.load_commit_history()
                    return
                else:
                    print("⚠️ Repo exists but has no commits — continuing setup.")
            else:
                print(f"🚀 Initializing Git at: {self.project_path}")
                subprocess.run(["git", "init"], cwd=self.project_path, env=self.custom_env(), check=True)

            self.open_in_daw_btn.setVisible(False)

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

            # ✅ Only make initial commit if repo has no commits yet
            self.bind_repo()
            if not self.repo.head.is_valid():
                subprocess.run(["git", "add", "."], cwd=self.project_path, env=self.custom_env(), check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.project_path, env=self.custom_env(), check=True)
                subprocess.run(["git", "branch", "-M", "main"], cwd=self.project_path, env=self.custom_env(), check=True)

                self.bind_repo()  # ✅ Rebind + update log + current commit

            QMessageBox.information(
                self,
                "Setup Complete",
                "🎶 Your project is now tracked with version control!\n\n"
                "You’re ready to loop, branch, and explore your musical ideas safely."
            )

            # ✅ Always call init_git afterward to sync state/UI
            self.init_git()
            self.open_in_daw_btn.setVisible(False)

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
                UNEXPECTED_ISSUE_MSG.format(error=str(e))
            )
        if hasattr(self, "branch_page"):
            self.branch_page.populate_branches()


    def connect_to_remote_repo(self):
        if not self.repo:
            QMessageBox.warning(self, NO_REPO_TITLE, NO_REPO_MSG)
            return

        url, ok = QInputDialog.getText(
            self,
            CONNECT_REMOTE_BTN,
            "Enter Git remote URL (e.g. https://github.com/user/repo.git):"
        )

        if not ok or not url.strip():
            return

        url = url.strip()

        try:
            # Add the remote (skip if already exists)
            existing = [r.name for r in self.repo.remotes]
            if "origin" in existing:
                self.repo.delete_remote("origin")

            self.repo.create_remote("origin", url)
            QMessageBox.information(self, REMOTE_ADDED_TITLE, REMOTE_ADDED_MSG.format(url=url))

            # Optionally push current branch
            if self.repo.head.is_valid():
                current_branch = self.repo.active_branch.name
                subprocess.run(
                    ["git", "push", "-u", "origin", current_branch],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )
                QMessageBox.information(
                    self, "Pushed",
                    f"🚀 Your current branch '{current_branch}' has been pushed to remote."
                )

        except Exception as e:
            QMessageBox.critical(self, REMOTE_SETUP_FAILED_TITLE, REMOTE_SETUP_FAILED_MSG.format(error=e))


    # Have removed the branch dropdown logic as the Load Alt Session button does the same thing
    # def on_branch_selected(self, index):
    #     if not self.repo or not hasattr(self, "branch_dropdown"):
    #         return

    #     selected_branch = self.branch_dropdown.itemText(index).strip()
    #     if selected_branch:
    #         self.switch_branch(selected_branch)


    def get_default_branch(self):
        try:
            if not self.repo.head.is_detached:
                return self.repo.active_branch.name
        except Exception:
            pass

        # Fallback to main/master
        for default in ["main", "master"]:
            if default in [h.name for h in self.repo.heads]:
                return default

        return self.repo.heads[0].name if self.repo.heads else "main"



    def safe_switch_branch(self, target_branch):
        # ✅ Detect uncommitted changes and trigger backup
        if self.repo.is_dirty(untracked_files=True):
            print("[SAFE SWITCH] Uncommitted changes detected — triggering backup.")
            if hasattr(self, "backup_unsaved_changes"):
                self.backup_unsaved_changes()
            return {"status": "warning", "message": "Uncommitted changes present — backed up."}

        try:
            # Check if target branch exists
            existing_branches = [b.name for b in self.repo.branches]
            if target_branch not in existing_branches:
                confirm = QMessageBox.question(
                    self,
                    CREATE_VERSION_LINE_TITLE,
                    CREATE_VERSION_LINE_MSG.format(branch=target_branch),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )
                if confirm != QMessageBox.StandardButton.Yes:
                    return {"status": "cancelled", "message": "User cancelled branch creation."}

                result = self.create_new_version_line(target_branch)

                # ✅ Handle fallback if UI fails but branch was created
                if result.get("status") not in ("ok", "success"):
                    print(f"[SAFE SWITCH] create_new_version_line failed: {result}")
                    if target_branch in [b.name for b in self.repo.branches]:
                        return {"status": "warning", "message": f"Branch '{target_branch}' created but with UI fallback."}
                    return {"status": "error", "message": result.get("message", "Failed to create new branch.")}

                return {"status": "ok", "message": f"Created and switched to new branch '{target_branch}'."}

            # If it already exists, just switch
            subprocess.run(
                ["git", "checkout", target_branch],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )
            self.bind_repo()
            self.init_git()
            self.load_commit_history()

            self.update_session_branch_display()
            return {"status": "ok", "message": f"Switched to branch '{target_branch}'."}

        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}



    def refresh_commit_table(self):
        """Stub method to satisfy tests — actual logic may be implemented later."""
        pass


    def update_branch_label(self):
        if self.repo.head.is_valid():
            try:
                branch = self.repo.active_branch.name
            except TypeError:
                branch = str(self.repo.head.ref) if self.repo.head.ref else "detached"
            self.branch_label.setText(f"Branch: {branch}")
        else:
            self.branch_label.setText(CURRENT_BRANCH_UNKNOWN)

    def update_commit_label(self):
        if self.repo.head.is_valid():
            short_sha = self.repo.head.commit.hexsha[:7]
            self.commit_label.setText(f"Commit: {short_sha}")
        else:
            self.commit_label.setText(CURRENT_COMMIT_UNKNOWN)

    def quick_commit(self):
        default_message = "Quick snapshot"
        self.commit_changes(commit_message=default_message)


    def commit_changes(self, commit_message=None):
        if not self.project_path or not self.git or not self.git.repo:
            print("[DEBUG] Skipping commit — no project or Git repo loaded")
            return {
                "status": "error",
                "message": "Cannot commit — no project or Git repo loaded."
            }

        is_test_mode = os.getenv("DAWGIT_TEST_MODE") == "1"

        if is_test_mode and commit_message == "":
            if hasattr(self, "_show_warning"):
                self._show_warning("You must enter a commit message.")
            return {"status": "error", "message": "Empty or cancelled commit message."}

        if is_test_mode and commit_message is None:
            pass  # Let monkeypatched dialog handle it

        if commit_message is None:
            commit_message, ok = QInputDialog.getText(
                self, COMMIT_CHANGES_BTN, "Enter commit message:"
            )
            if not ok or not isinstance(commit_message, str) or not commit_message.strip():
                if hasattr(self, "_show_warning"):
                    self._show_warning("Commit cancelled. Please enter a valid commit message.")
                return {"status": "error", "message": "Empty or cancelled commit message."}

        result = self.git.commit_changes(commit_message)

        if result["status"] != "success":
            if "nothing to commit" in result.get("message", ""):
                self._show_warning(
                    "🎧 No changes to commit.\n\n"
                    "It looks like your DAW project hasn’t changed since your last snapshot.\n"
                    "Make a small edit and save your session before trying again."
                )
            else:
                self._show_error(f"Commit failed: {result['message']}")
            return result

        short_sha = result["sha"][:7]
        self.current_commit_id = result["sha"]

        # ✅ Push to remote if enabled
        if hasattr(self.setup_page, "remote_checkbox") and self.setup_page.remote_checkbox.isChecked():
            try:
                print("[DEBUG] Attempting to push to remote...")
                subprocess.run(
                    # ["git", "push", "origin", self.get_current_branch()],
                    ["git", "push", "origin", self.get_default_branch()],

                    cwd=self.project_path,
                    env=self.custom_env(),
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"[DEBUG] Remote push failed: {e}")
                QMessageBox.critical(
                    self,
                    "Push Failed",
                    f"Couldn’t push to remote:\n\n{e}"
                )

        if hasattr(self, "commit_message"):
            self.commit_message.setPlainText("")


        # Update UI state
        self.update_log()
        self.update_branch_label()
        self.update_commit_label()
        self.update_status_label()

        try:
            branch = self.repo.active_branch.name
        except TypeError:
            branch = str(self.repo.head.ref) if self.repo.head.ref else "detached"

        QMessageBox.information(self, COMMIT_SUCCESS_TITLE, COMMIT_SUCCESS_MSG.format(branch=branch, sha=short_sha))


        if hasattr(self, "project_marker") and self.repo.head.is_valid():
            msg = self.repo.head.commit.message.strip()
            self.project_marker.setdefault("repository_info", {})["last_commit_sha"] = result["sha"]
            self.project_marker["repository_info"]["last_commit_message"] = msg
            self.save_project_marker()

        return {"status": "success", "sha": short_sha, "branch": branch}


    def update_snapshot_status_labels(self):
        """Update all relevant status labels with the current editing state."""
        if not self.repo:
            return

        is_detached = self.repo.head.is_detached
        branch = self.repo.active_branch.name if not is_detached else "detached"

        try:
            commit_count = len(list(self.repo.iter_commits()))
        except Exception:
            commit_count = "?"

        label = (
            STATUS_BRANCH_TAKE.format(branch=branch, take=commit_count)
            if not is_detached
            else SNAPSHOT_DETACHED_WARNING
        )

        self.status_label.setText(label)
        if hasattr(self.snapshot_page, "status_label"):
            self.snapshot_page.status_label.setText(label)


    def _create_editable_snapshot_copy(self):
        """Creates a safe editable copy of the current .als file into .dawgit_checkout_work/"""
        try:
            editable_dir = Path(self.project_path) / ".dawgit_checkout_work"
            editable_dir.mkdir(exist_ok=True)
            als_files = list(Path(self.project_path).glob("*.als"))

            if als_files:
                als_file = als_files[0]
                editable_name = f"{self.project_path.name}_editable.als"
                editable_path = editable_dir / editable_name
                shutil.copy2(als_file, editable_path)
                self.editable_checkout_path = editable_path
                print(f"[DEBUG] Created editable snapshot copy at: {editable_path}")
                return editable_path
            else:
                print("[WARN] No .als file found for editable copy.")
                return None
        except Exception as e:
            print(f"[ERROR] Editable snapshot creation failed: {e}")
            return None




    def update_role_buttons(self):
        """
        Enable/disable role assignment buttons based on Git HEAD state.
        Update tooltips accordingly to guide the user.
        """
        if not self.repo or not self.repo.head.is_valid():
            return

        in_detached = self.repo.head.is_detached

        # ✅ Modular CommitPage buttons — handle all current tag buttons cleanly
        if hasattr(self, "commit_page"):
            for attr in ["tag_main_btn", "tag_creative_btn", "tag_alt_btn", "tag_custom_btn"]:
                btn = getattr(self.commit_page, attr, None)
                if btn:
                    btn.setEnabled(not in_detached)
                    btn.setToolTip(
                        "❌ Tagging is only available on active version lines."
                        if in_detached else ""
                    )



    def show_current_commit(self):
        if not self.repo or not self.repo.head.is_valid():
            QMessageBox.information(self, COMMIT_INFO_TITLE, COMMIT_INFO_EMPTY)
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
        QMessageBox.information(self, CURRENT_COMMIT_TITLE, body)

    
    def create_new_version_line(self, branch_name: str):
        if not self.project_path:
            return {"status": "error", "message": "No project path set"}

        try:
            if self.repo is None:
                self.repo = Repo(self.project_path)

            # 🎯 Detach HEAD to snapshot commit before creating a new branch
            if not self.repo.head.is_detached:
                self.repo.git.checkout(self.repo.head.commit.hexsha)

            # ✅ Step 1: Create marker file
            marker_path = Path(self.project_path) / ".version_marker"
            marker_path.write_text("🎼 Auto-created marker")
            files_to_commit = [marker_path.relative_to(self.project_path).as_posix()]

            # ✅ Step 2: Create placeholder DAW file if none exist
            daw_files = list(Path(self.project_path).glob("*.als")) + list(Path(self.project_path).glob("*.logicx"))
            if not daw_files:
                if self.repo.head.is_detached:
                    placeholder_path = Path(self.project_path) / "auto_placeholder.als"
                    placeholder_path.write_text("Temporary placeholder for version line start")
                    files_to_commit.append(placeholder_path.relative_to(self.project_path).as_posix())
                else:
                    return {
                        "status": "error",
                        "message": "No DAW files found for new version line, and not in detached state"
                    }

            # ✅ Step 3: Create or switch to branch safely
            branch = None
            if branch_name in self.repo.branches:
                print(f"[DEBUG] Branch '{branch_name}' already exists — switching")
                branch = self.repo.branches[branch_name]
            else:
                branch = self.repo.create_head(branch_name)

            branch.checkout()

            # ✅ Step 4: Commit marker and placeholder
            try:
                print(f"[DEBUG] Committing files: {files_to_commit}")
                self.repo.index.add(files_to_commit)
                commit_message = f"🎼 Start New Version Line: {branch_name}"
                self.repo.index.commit(commit_message)
            except Exception as e:
                print(f"[ERROR] Failed to commit new version line: {e}")
                return {"status": "error", "message": f"Commit failed: {e}"}

            # ✅ Step 5: Optional remote push
            if (
                hasattr(self, "setup_page") and
                hasattr(self.setup_page, "remote_checkbox") and
                self.setup_page.remote_checkbox.isChecked()
            ):
                try:
                    print("[DEBUG] Attempting to push to remote...")
                    subprocess.run(
                        ["git", "push", "origin", branch_name],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"[DEBUG] Remote push failed: {e}")
                    QMessageBox.critical(
                        self,
                        "Push Failed",
                        f"Couldn’t push to remote:\n\n{e}"
                    )

            # ✅ Step 6: Refresh UI and status
            self.current_branch = self.repo.active_branch.name
            if hasattr(self, "update_log"):
                self.update_log()
            if hasattr(self, "update_status_label"):
                self.update_status_label()
            if hasattr(self, "update_role_buttons"):
                self.update_role_buttons()

            return {
                "status": "success",
                "branch": branch_name,
                "commit_message": commit_message
            }

        except Exception as e:
            print(f"[ERROR] create_new_version_line: {e}")
            return {"status": "error", "message": str(e)}




    def show_commit_context_menu(self, position):
        row = self.snapshot_page.commit_table.rowAt(position.y())
        if row == -1:
            return

        self.snapshot_page.commit_table.selectRow(row)

        commit_item = self.snapshot_page.commit_table.item(row, 2)
        commit_sha = commit_item.toolTip() if commit_item else None

        if not commit_sha:
            commit_sha = self.current_commit_id

        if not commit_sha:
            return  # gracefully bail, no warning needed for context menu

        menu = QMenu(self)
        delete_action = QAction("🗑️ Delete This Snapshot", self)

        # Check if commit is reachable from current branch
        try:
            reachable = [c.hexsha for c in self.repo.iter_commits()]
            if commit_sha not in reachable:
                delete_action.setEnabled(False)
                delete_action.setToolTip(CROSS_BRANCH_COMMIT_MSG)
        except Exception as e:
            print(f"[WARN] Could not validate commit reachability: {e}")

        delete_action.triggered.connect(self.delete_selected_commit)
        menu.addAction(delete_action)
        menu.exec(self.snapshot_page.commit_table.viewport().mapToGlobal(position))


    def update_session_branch_display(self):
        """Updates the labels showing current branch and commit status."""
        if not self.repo:
            return

        try:
            # Branch name
            if self.repo.head.is_detached:
                branch = "(detached)"
            else:
                branch = self.repo.active_branch.name

            # Always compute display name to avoid unbound errors
            display_branch = self.normalize_branch_name(branch)

            # Commit ID
            sha = self.repo.head.commit.hexsha[:7] if self.repo.head.is_valid() else "unknown"

            # Set the UI labels
            if hasattr(self, "branch_label"):
                self.branch_label.setText(
                    STATUS_BRANCH_TAKE.format(
                        branch=display_branch,
                        take=self.get_current_take_name()
                    )
                )

            if hasattr(self, "commit_label"):
                self.commit_label.setText(f"🎶 Commit: {sha}")

        except Exception as e:
            print(f"[DEBUG] Error updating session display: {e}")



  

    def update_version_line_label(self):
        try:
            branch_name = self.repo.active_branch.name
            label_text = f"🎼 You're working on Version Line: {branch_name.upper()}"
        except Exception:
            label_text = SNAPSHOT_NO_VERSION_LINE

        # 🧪 Test mode fallback
        if hasattr(self, "version_line_label"):
            self.version_line_label.setText(label_text)

        # 🖼️ Full UI mode
        if hasattr(self, "snapshot_page") and hasattr(self.snapshot_page, "version_line_label"):
            self.snapshot_page.version_line_label.setText(label_text)



    def delete_selected_commit(self):
        table = (
            getattr(self.snapshot_page, "commit_table", None)
            if hasattr(self, "snapshot_page") else None
        ) or getattr(self, "history_table", None)

        if not table:
            print("[TEST] No commit table found")
            return

        row = table.currentRow()
        if row == -1:
            QMessageBox.warning(self, NO_SELECTION_TITLE, "Please select a snapshot to delete.")
            return

        commit_id = table.item(row, 1).toolTip()
        commit_msg = table.item(row, 2).text()
        confirm = QMessageBox.question(
            self,
            DELETE_SNAPSHOT_TITLE,
            DELETE_SNAPSHOT_MSG.format(msg=commit_msg[:60]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            if self.has_unsaved_changes():
                self.backup_unsaved_changes()

            # Locate commit and parent
            all_commits = list(self.repo.iter_commits("HEAD", max_count=50))
            target_commit = next((c for c in all_commits if c.hexsha.startswith(commit_id[:7])), None)
            if not target_commit:
                raise Exception("Commit not found in history.")

            if not target_commit.parents:
                QMessageBox.warning(self, CANT_DELETE_ROOT_TITLE, "The very first commit in the repo cannot be deleted.")
                return

            parent_sha = target_commit.parents[0].hexsha

            # Rebase to drop commit
            subprocess.run(
                ["git", "rebase", "--onto", parent_sha, target_commit.hexsha],
                cwd=self.project_path,
                env=self.custom_env(),
                check=True
            )

            self.repo = Repo(self.project_path)
            self.repo.git.checkout(self.repo.active_branch.name)
            self.init_git()
            self.load_commit_history()
            if hasattr(self, "commit_page"):
                is_detached = self.repo.head.is_detached
                in_editable = ".dawgit_checkout_work" in str(self.project_path)
                if is_detached and not in_editable:
                    self.commit_page.set_commit_controls_enabled(False, SNAPSHOT_EDIT_BLOCK_TOOLTIP)
                else:
                    self.commit_page.set_commit_controls_enabled(True, "")

            self.status_message("🗑️ Snapshot deleted using rebase --onto.")
            # self.open_latest_daw_project()

        except Exception as e:
            QMessageBox.critical(self, DELETE_FAILED_TITLE, f"Failed to delete commit:\n{e}")


    def als_recently_modified(self, threshold_seconds=60):
        als_file = next(Path(self.project_path).glob("*.als"), None)
        if als_file and als_file.exists():
            modified_time = als_file.stat().st_mtime
            time_since_mod = time.time() - modified_time
            return time_since_mod < threshold_seconds
        return False

    
    def get_latest_daw_project_file(self):
        """Return the most recently modified .als or .logicx file, skipping placeholders and test files."""
        path = Path(self.repo.working_tree_dir)
        daw_files = sorted(
            list(path.glob("*.als")) + list(path.glob("*.logicx")),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        # First pass: skip placeholders and test files
        for f in daw_files:
            name = f.name.lower()
            if not name.startswith("auto_placeholder") and not name.startswith("test"):
                return str(f)

        # Fallback: just return the most recent one, even if it's a placeholder
        return str(daw_files[0]) if daw_files else None



    def open_latest_daw_project(self):
        # ✅ NEW: Launch editable snapshot directly and skip modal
        editable = getattr(self, "editable_checkout_path", None)
        if editable and Path(editable).exists():
            try:
                subprocess.Popen(["open", str(editable)])
                print(f"[DEBUG] Opened editable snapshot in DAW: {editable}")
                return
            except Exception as e:
                print(f"[WARN] Failed to open editable copy: {e}")
                # Fall through to regular warning/modal logic

        # ✅ Delay warning until user actually tries to open in DAW
        if self.als_recently_modified() and os.getenv("DAWGIT_TEST_MODE") != "1":
            confirm = QMessageBox.question(
                self,
                ABLETON_MAY_BE_OPEN_TITLE,
                ABLETON_MAY_BE_OPEN_MSG,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        # ✅ Skip snapshot dialog if testing
        if self.repo and self.repo.head.is_detached:
            if os.getenv("DAWGIT_TEST_MODE") == "1":
                print("[TEST MODE] Skipping snapshot confirmation.")
            else:
                confirm = QMessageBox.question(
                    self,
                    SNAPSHOT_CONFIRMATION_TITLE,
                    SNAPSHOT_CONFIRMATION_MSG,
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                )

                if confirm != QMessageBox.StandardButton.Ok:
                    print(f"[DEBUG] Early exit at snapshot confirmation")
                    return


        # ✅ NEW: Prefer editable snapshot copy if it exists
        editable = getattr(self, "editable_checkout_path", None)
        if editable and Path(editable).exists():
            try:
                subprocess.Popen(["open", str(editable)])
                print(f"[DEBUG] Opened editable snapshot in DAW: {editable}")
                return
            except Exception as e:
                print(f"[WARN] Failed to open editable copy: {e}")
                # Fallback continues to original logic

        repo_path = Path(self.repo.working_tree_dir)
        daw_files = list(repo_path.glob("*.als")) + list(repo_path.glob("*.logicx"))

        if not daw_files:
            self._show_warning("No DAW project file (.als or .logicx) found in this version.")
            print(f"[DEBUG] Early exit: no DAW files")
            return

        daw_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        latest_file = daw_files[0]

        if (
            os.getenv("DAWGIT_TEST_MODE") != "1"
            and (
                latest_file.name.startswith("test_")
                or "placeholder" in latest_file.name.lower()
                or "pytest-of-" in str(latest_file)
            )
        ):
            print(f"[DEBUG] Skipping test/placeholder file: {latest_file}")
            return

        try:
            if os.getenv("DAWGIT_TEST_MODE") == "1":
                return {"status": "success", "opened_file": str(latest_file)}

            safe_path = str(latest_file.resolve())
            subprocess.Popen(["open", safe_path])  # ✅ Safe
        except Exception as e:
            self._show_error(f"Failed to open project file:\n{e}")




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
            self.load_commit_history()

            # self.open_latest_daw_project()

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, REBASE_FAILED_TITLE, f"Git error:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, UNEXPECTED_ERROR_TITLE, f"❌ {e}")


    def get_commit_sha(app, row):
        """
        Extract the commit SHA from a given table row (tooltip in column 1).
        """
        try:
            item = app.history_table.item(row, 1)  # SHA column
        except Exception as e:
            print(f"[TEST ERROR] Failed to get item at row {row}, column 1: {e}")
            return None

        if item is None:
            print(f"[TEST ERROR] No item at row {row}, column 1")
            return None

        sha = item.toolTip()
        if not sha:
            print(f"[TEST ERROR] Empty tooltip at row {row}, column 1")
            return None

        return sha

    
    def _set_commit_id_from_selected_row(self):
        selected_items = self.snapshot_page.commit_table.selectedItems()
        if not selected_items:
            print("[WARN] No items selected in history table.")
            self.current_commit_id = None
            return

        for item in selected_items:
            if item.column() == 2:  # ✅ Column 2 = Commit ID column
                sha = item.toolTip()
                print(f"[DEBUG] Selected row = {item.row()}, SHA = {sha}")
                if sha and isinstance(sha, str) and sha.strip():
                    self.current_commit_id = sha
                    print(f"[DEBUG] ✅ SHA set from selected row: {sha}")
                    self.snapshot_page.commit_table.scrollToItem(
                        item, QAbstractItemView.ScrollHint.PositionAtCenter
                    )
                    return

        print("[WARN] No SHA found in selected items.")
        self.current_commit_id = None        


    def save_settings(self):
        """
        Saves commit roles to a local JSON config file for persistence across sessions.
        """
        settings_path = self.project_path / ".dawgit_settings.json"
        with open(settings_path, "w") as f:
            json.dump({"commit_roles": self.commit_roles}, f)


    # def load_settings(self):
    #     settings_path = self.project_path / ".dawgit_settings.json"
    #     if settings_path.exists():
    #         with open(settings_path, "r") as f:
    #             try:
    #                 data = json.load(f)
    #                 self.commit_roles = data.get("commit_roles", {})
    #             except json.JSONDecodeError:
    #                 self.commit_roles = {}
    #     else:
    #         self.commit_roles = {}
    #         self.load_commit_roles()


    def save_commit_roles(self):
        """
        Saves the commit role mapping to a hidden JSON file in the project directory.
        """
        if self.project_path:
            meta_file = Path(self.project_path) / ".dawgit_roles.json"
            try:
                with open(meta_file, "w") as f:
                    json.dump(self.commit_roles, f)
                print(f"[DEBUG] Saved commit roles to {meta_file}")
            except Exception as e:
                print(f"[ERROR] Failed to save commit roles: {e}")


    def assign_commit_role(self, commit_sha: str, role: str):
        """
        Assigns a role to a commit and saves the mapping.
        """
        if not commit_sha:
            print("[ERROR] Cannot assign role — invalid commit SHA:", commit_sha)
            return

        if not hasattr(self, "commit_roles"):
            self.commit_roles = {}

        self.commit_roles[commit_sha] = role
        print(f"[DEBUG] Role '{role}' assigned to commit {commit_sha}")  # Log the assignment

        # Save the updated commit_roles to disk
        self.save_commit_roles()
        print(f"[DEBUG] Assigned role '{role}' to commit {commit_sha}")
        self.show_status_message(f"🎧 Snapshot tagged as '{role}': {commit_sha[:7]}")

        # ✅ Update marker
        if hasattr(self, "project_marker"):
            self.project_marker.setdefault("repository_info", {}).setdefault("commit_roles", {})[commit_sha] = role
            self.save_project_marker()


    def load_commit_roles(self):
        if not self.project_path:
            print("[DEBUG] Skipping role load — no project path set.")
            self.commit_roles = {}
            return

        roles_path = Path(self.project_path) / ".dawgit_roles.json"
        if roles_path.exists():
            try:
                with roles_path.open("r") as f:
                    self.commit_roles = json.load(f)
                    print(f"[DEBUG] Loaded commit roles from {roles_path}")
            except Exception as e:
                print(f"[ERROR] Failed to load commit roles: {e}")
                self.commit_roles = {}
        else:
            print(f"[DEBUG] No commit role file found at {roles_path}")
            self.commit_roles = {}


    @pyqtSlot()
    def tag_custom_label(self):
        """
        Prompts user for a custom label and assigns it to the selected commit.
        """
        self._set_commit_id_from_selected_row()
        row = self.snapshot_page.commit_table.currentRow()
        if row < 0:
            self._show_warning("Please select a snapshot to tag.")
            return

        commit_item = self.snapshot_page.commit_table.item(row, 2)
        sha = commit_item.toolTip() if commit_item else self.current_commit_id

        if not sha:
            self._show_warning("Commit SHA missing — can't assign role.")
            return

        label, ok = QInputDialog.getText(
            self,
            TAG_SNAPSHOT_BTN,
            "Enter a label (e.g., 'alt_take', 'pre_master', 'idea_A'):\n\n"
            "✅ Letters, numbers, dashes, underscores only.\n"
            "🚫 No spaces or special characters."
        )

        if not ok:
            return

        # ✅ Sanitize and validate
        label = label.strip().lower().replace(" ", "_")
        label = "".join(c for c in label if c.isalnum() or c in ("_", "-"))

        if not label:
            QMessageBox.warning(self, INVALID_LABEL_TITLE, INVALID_LABEL_MSG)
            return

        clean_label = label.strip()
        self.current_commit_id = sha
        self.assign_commit_role(sha, clean_label)
        self.save_commit_roles()
        self.status_message(f"✏️ Commit tagged as '{clean_label}': {sha[:7]}")

        if os.getenv("DAWGIT_TEST_MODE") == "1":
            print("[DEBUG] DAWGIT_TEST_MODE active — running load_commit_history directly")
            self.load_commit_history()
        else:
            QTimer.singleShot(100, self.load_commit_history)


    @pyqtSlot()
    def tag_main_mix(self):
        """
        Assigns the 'ROLE_KEY_MAIN_MIX' role to the currently selected commit.
        Ensures only one commit can hold the 'ROLE_KEY_MAIN_MIX' tag at a time.
        """
        self._set_commit_id_from_selected_row()
        row = self.snapshot_page.commit_table.currentRow()
        if row < 0:
            self._show_warning(f"Please select a snapshot to tag as '{ROLE_KEY_MAIN_MIX}'.")
            return

        commit_item = self.snapshot_page.commit_table.item(row, 2)
        sha = commit_item.toolTip() if commit_item else self.current_commit_id

        if not sha:
            self._show_warning("Commit SHA missing — can't assign role.")
            return

        # 🧼 Remove existing 'main_mix' tag from another commit, if needed
        existing_main = next((k for k, v in self.commit_roles.items() if v == ROLE_KEY_MAIN_MIX and k != sha), None)

        if existing_main and os.getenv("DAWGIT_TEST_MODE") != "1":
            old_msg = self.repo.commit(existing_main).message.strip().split("\n")[0][:40]
            new_msg = self.repo.commit(sha).message.strip().split("\n")[0][:40]

            confirm = QMessageBox.question(
                self,
                CONFIRM_REPLACE_MAIN_TITLE,
                CONFIRM_REPLACE_MAIN_MSG.format(
                    old_sha=existing_main[:7],
                    old_msg=old_msg,
                    new_sha=sha[:7],
                    new_msg=new_msg
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return

            self.commit_roles.pop(existing_main, None)

        self.current_commit_id = sha
        self.assign_commit_role(sha, ROLE_KEY_MAIN_MIX)
        self.save_commit_roles()
        self.status_message(STATUS_TAGGED_AS_MAIN_MIX.format(sha=sha[:7]))

        if os.getenv("DAWGIT_TEST_MODE") == "1":
            print("[DEBUG] DAWGIT_TEST_MODE active — running load_commit_history directly")
            self.load_commit_history()
        else:
            QTimer.singleShot(100, self.load_commit_history)


    @pyqtSlot()
    def tag_creative_take(self):  
        print("[DEBUG] 🚨 tag_creative_take() fired")
        """
        Assigns the 'creative_take' role to the currently selected commit.
        """
        self._set_commit_id_from_selected_row()
        row = self.snapshot_page.commit_table.currentRow()

        if row < 0:
            self._show_warning(f"Please select a snapshot to tag as '{ROLE_KEY_CREATIVE_TAKE}'.")
            return  # ✅ only return inside this block

        commit_item = self.snapshot_page.commit_table.item(row, 2)
        sha = commit_item.toolTip() if commit_item else self.current_commit_id

        if not sha:
            self._show_warning("Commit SHA missing — can't assign role.")
            return  # ✅ needed here too

        # ✅ Normalized internal label
        safe_label = "creative_take"

        self.current_commit_id = sha
        self.assign_commit_role(sha, safe_label)
        self.save_commit_roles()
        self.status_message(f"🎨 Commit tagged as '{safe_label}': {sha[:7]}")

        if os.getenv("DAWGIT_TEST_MODE") == "1":
            print("[DEBUG] DAWGIT_TEST_MODE active — running load_commit_history directly")
            self.load_commit_history()
        else:
            QTimer.singleShot(100, self.load_commit_history)


    @pyqtSlot()
    def tag_alt_mix(self):
        """
        Assigns the 'alt_mixdown' role to the currently selected commit.
        """
        self._set_commit_id_from_selected_row()
        row = self.snapshot_page.commit_table.currentRow()
        if row < 0:
            self._show_warning(f"Please select a snapshot to tag as '{ROLE_KEY_ALT_MIXDOWN}'.")
            return

        commit_item = self.snapshot_page.commit_table.item(row, 2)
        sha = commit_item.toolTip() if commit_item else self.current_commit_id

        if not sha:
            self._show_warning("Commit SHA missing — can't assign role.")
            return

        # ✅ Normalized internal label
        safe_label = "alt_mixdown"

        self.current_commit_id = sha
        self.assign_commit_role(sha, safe_label)
        self.save_commit_roles()
        self.status_message(f"🎛️ Commit tagged as '{safe_label}': {sha[:7]}")

        if os.getenv("DAWGIT_TEST_MODE") == "1":
            print("[DEBUG] DAWGIT_TEST_MODE active — running load_commit_history directly")
            self.load_commit_history()
        else:
            QTimer.singleShot(100, self.load_commit_history)


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
                "\n\n📦 Snapshot loaded — read-only mode.\n"
                "You can explore safely.\n\n"
                "🎼 To keep working, start a new version line from here."
            )       
            title = "Viewing Snapshot"
        else:
            title = "Switched Version"

        QMessageBox.information(self, title, body)
    

    def auto_commit(self, message: str, tag: str = ""):
        if not self.repo:
            QMessageBox.warning(self, NO_REPO_TITLE, NO_REPO_SAVE_MSG)
            return

        # ✅ Immediately disable UI to prevent double clicks
        if hasattr(self, "auto_save_toggle") and self.auto_save_toggle:
            self.auto_save_toggle.setEnabled(False)
            self.auto_save_toggle.setEnabled(False)
            self.auto_save_toggle.setToolTip(SAVING_SNAPSHOT_LABEL)

        if hasattr(self, "snapshot_button") and self.snapshot_button:
            self.snapshot_button.setEnabled(False)
            self.snapshot_button.setToolTip(SAVING_SNAPSHOT_LABEL)

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
            commit_sha = commit.hexsha

            if tag:
                if tag in [t.name for t in self.repo.tags]:
                    print(f"⚠️ Tag '{tag}' already exists. Skipping tag creation.")
                else:
                    self.repo.create_tag(tag, ref=commit_sha)

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

            self.load_commit_history()
            self.update_status_label()
            self.show_status_message("✅ Auto-committed: Auto snapshot")

            # ✅ Update tooltips to reflect final state
            if hasattr(self, "auto_save_toggle") and self.auto_save_toggle:
                self.auto_save_toggle.setToolTip(SNAPSHOT_SAVED_AUTODISABLED)

            if hasattr(self, "snapshot_button") and self.snapshot_button:
                self.snapshot_button.setToolTip(SNAPSHOT_SAVED_WAITING_TOOLTIP)

            # Final confirmation
            msg = f"✅ Auto-commit completed:\n\n{message}"
            QMessageBox.information(self, AUTO_SAVE_TITLE, msg)
            print(f"✅ Auto-committed: {message}")

            # ✅ Refresh UI state to re-enable if new changes
            if hasattr(self, "refresh_ui_state"):
                self.refresh_ui_state()

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


    def normalize_branch_name(self, name: str) -> str:
        return "MAIN" if name == "main" else name


    def switch_to_branch_ui(self, branch_name: str):
        # 👇 Convert display name back to real Git branch name
        branch_name = self.normalize_branch_name(branch_name)
        result = self.switch_branch(branch_name)

        if result.get("status") == "success":
            # Try to get .version_marker or latest commit message
            marker_path = Path(self.repo.working_tree_dir) / ".version_marker"
            if marker_path.exists():
                take_label = marker_path.read_text().strip()
            else:
                try:
                    commit = self.repo.head.commit
                    msg = commit.message.strip()
                    take_label = msg if len(msg) < 60 else "(Unnamed Take)"
                except Exception:
                    take_label = "(Unknown)"

            self.branch_label.setText(f"Version Line: {branch_name.upper()} • Current take: {take_label}")

        else:
            self._show_warning(result.get("message", "Failed to switch session."))


    def get_branch_take_label(self, branch_name: str) -> str:
        try:
            # Checkout the branch in detached mode to inspect its version marker
            current = self.repo.head.commit.hexsha
            temp_branch = f"_dawgit_temp_inspect_{branch_name}"

            self.repo.git.switch("--detach")
            self.repo.git.checkout(branch_name)

            marker_path = Path(self.repo.working_tree_dir) / ".version_marker"
            if marker_path.exists():
                label = marker_path.read_text().strip()
            else:
                label = self.repo.head.commit.message.strip()

            # Return to original commit
            self.repo.git.checkout(current)

            return label if label else "(no label)"
        except Exception as e:
            print(f"[WARN] Could not load take label for branch {branch_name}: {e}")
            return "(unknown)"


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
        """⬅️ Checkout a specific commit by SHA or from selected table row, even if benign files exist."""
        result = {"status": "success"}

        if not commit_sha:
            selected_row = self.snapshot_page.commit_table.currentRow()
            if selected_row < 0:
                current_sha = self.repo.head.commit.hexsha[:7] if self.repo else "unknown"
                if self.sender():
                    QMessageBox.information(self, NO_SNAPSHOT_SELECTED_TITLE, NO_SNAPSHOT_SELECTED_MSG)
                return {"status": "cancelled", "message": "No version selected."}

            print(f"[DEBUG] selected_row = {selected_row}")
            sha_col = 2
            commit_item = self.snapshot_page.commit_table.item(selected_row, sha_col)
            if not commit_item:
                for col in range(self.snapshot_page.commit_table.columnCount()):
                    item = self.snapshot_page.commit_table.item(selected_row, col)
                    if item and len(item.text()) == 7:
                        commit_item = item
                        break
            if not commit_item:
                QMessageBox.warning(self, COMMIT_NOT_FOUND_TITLE, "❌ Could not find a valid commit at this row.")
                return {"status": "error", "message": "No commit item found."}

            print(f"[DEBUG] commit_item.text = {commit_item.text()}")
            print(f"[DEBUG] commit_item.toolTip = {commit_item.toolTip()}")

            commit_sha = commit_item.toolTip().strip() if commit_item.toolTip() else self._get_full_sha(commit_item.text().strip())


            if not commit_sha:
                return {"status": "error", "message": "No SHA available in commit row."}

        try:
            # ✅ Ignore tracked noise files via helper
            relevant_dirty = self.get_relevant_dirty_files()
            print(f"[DEBUG] Filtered relevant_dirty files: {relevant_dirty}")

            if relevant_dirty:
                print(f"[BLOCK] Dirty files detected: {relevant_dirty}")
                file_list = "\n".join(f"• {f}" for f in relevant_dirty)

                QMessageBox.warning(
                    self,
                    UNSAFE_DIRTY_EDITS_TITLE,
                    UNSAFE_DIRTY_EDITS_MSG.format(file_list=file_list)
                )
                return {"status": "blocked", "files": relevant_dirty}

            # ⛔ Skip if already on this commit

            if commit_sha.startswith(self.repo.head.commit.hexsha[:7]):
                QMessageBox.information(
                    self,
                    ALREADY_ON_COMMIT_TITLE,
                    ALREADY_ON_COMMIT_MESSAGE.format(sha=commit_sha[:7])
                )
                return {"status": "noop", "message": "Already on this commit."}

            # 🧠 Backup latest state before switching
            try:
                from daw_git_core import backup_latest_commit_state
                if self.repo and self.project_path:
                    backup_latest_commit_state(self.repo, Path(self.project_path))
            except Exception as e:
                print(f"[WARN] Snapshot backup failed: {e}")

            # 🔧 Discard tracked noise files
            safe_to_reset = {".DS_Store", "PROJECT_MARKER.json", ".dawgit_roles.json"}
            reset_targets = [p.a_path for p in self.repo.index.diff(None) if Path(p.a_path).name in safe_to_reset]
            if reset_targets:
                print(f"[DEBUG] Resetting safe dirty files: {reset_targets}")
                subprocess.run(["git", "checkout", "--"] + reset_targets, cwd=self.project_path, env=self.custom_env(), check=True)

            subprocess.run(["git", "checkout", commit_sha], cwd=self.project_path, env=self.custom_env(), check=True)
            subprocess.run(["git", "lfs", "checkout"], cwd=self.project_path, env=self.custom_env(), check=True)

            self.bind_repo()
            self.init_git()
            self.load_commit_history()
            self.update_role_buttons()

            self.current_commit_id = self.repo.head.commit.hexsha
            self.show_commit_checkout_info(self.repo.commit(commit_sha))

            # Highlight selected commit
            for row in range(self.snapshot_page.commit_table.rowCount()):
                item = self.snapshot_page.commit_table.item(row, 2)
                if item and commit_sha.startswith(item.toolTip() or item.text()):
                    self.snapshot_page.commit_table.selectRow(row)
                    self.snapshot_page.commit_table.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)
                    break

            # ✅ Create editable snapshot copy
            editable_path = self._create_editable_snapshot_copy()
            self.editable_checkout_path = editable_path if editable_path else None
            print("[INFO] Snapshot checkout completed — editable copy created (not auto-launched)")


            self.update_snapshot_status_labels()

            # ✅ Show success message
            if hasattr(self.snapshot_page, "status_label"):
                self.snapshot_page.status_label.setText(
                    f"✅ Snapshot {commit_sha[:7]} loaded — read-only mode. Explore or start a new version line."
                )
            self.open_in_daw_btn.setVisible(True)

            # ✅ Show success message
            if hasattr(self.snapshot_page, "status_label"):
                self.snapshot_page.status_label.setText(
                    f"✅ Snapshot {commit_sha[:7]} loaded — read-only mode. Explore or start a new version line."
                )
            self.open_in_daw_btn.setVisible(True)

            # 🧠 Update commit UI state
            if hasattr(self.commit_page, "update_snapshot_editing_state"):
                self.commit_page.update_snapshot_editing_state()

            if hasattr(self, "commit_page"):
                is_detached = self.repo.head.is_detached
                in_editable = ".dawgit_checkout_work" in str(self.project_path)
                if is_detached and not in_editable:
                    self.commit_page.set_commit_controls_enabled(
                        False,
                        "🎧 Snapshot mode: You’re previewing an old take. Start a new version to edit and save in your DAW."
                    )
                else:
                    self.commit_page.set_commit_controls_enabled(True, "")

            self.update_session_status_mode()
            return result
        

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, CHECKOUT_FAILED_TITLE, f"❌ Could not switch versions:\n\n{e}")
            return {"status": "error", "message": str(e)}

        except Exception as e:
            QMessageBox.critical(self, UNEXPECTED_ERROR_TITLE, f"⚠️ Unexpected error:\n\n{e}")
            return {"status": "error", "message": str(e)}


    def _get_full_sha(self, short_sha):
        """Return full-length SHA given a short version."""
        try:
            return next((c.hexsha for c in self.repo.iter_commits() if c.hexsha.startswith(short_sha)), short_sha)
        except Exception as e:
            print(f"[WARN] Could not resolve full SHA from short SHA '{short_sha}': {e}")
            return short_sha



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
                    SNAPSHOT_SWITCH_WARNING_TITLE,
                    SNAPSHOT_SWITCH_WARNING_MSG,
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
                        UNSAVED_CHANGES_TITLE,
                        UNSAVED_CHANGES_MSG,
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    ) == QMessageBox.StandardButton.Yes:                        self.backup_unsaved_changes()
                    subprocess.run(
                        ["git", "stash", "push", "-u", "-m", "DAWGitApp auto-stash"],
                        cwd=self.project_path,
                        env=self.custom_env(),
                        check=True
                    )
                    

                self.repo.git.checkout(selected)
                self.current_commit_id = self.repo.head.commit.hexsha
                self.load_commit_history()

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
        if isinstance(self.project_path, str):
            self.project_path = Path(self.project_path)

        try:
            if not self.repo or not self.project_path:
                return False

            # ✅ Known noise files to ignore
            excluded_patterns = [
                "Ableton Project Info/*",
                "*.asd", "*.tmp", "*.bak", "*.log", "*.swp",
                ".DS_Store", "._*", "auto_placeholder.als",
                "PROJECT_MARKER.json", ".dawgit_roles.json",
                "PROJECT_STATUS.md", ".gitattributes",
                ".gitignore", ".*", "Icon\r", '"Icon\r"', "Icon?", "Icon\\r"
            ]


            self.repo.git.clear_cache()
            status_output = self.repo.git.status("--porcelain").splitlines()

            for line in status_output:
                if len(line) < 4:
                    continue

                file_path_raw = line[3:].strip()
                file_path_clean = file_path_raw.strip('"').strip()

                # 🔍 Debug raw and cleaned value
                if os.getenv("DAWGIT_DEBUG") == "1":
                    print(f"[DEBUG] Raw path: {repr(file_path_raw)} → Cleaned: {repr(file_path_clean)}")

                # 🚫 Ignore any Icon variants with raw or escaped carriage returns
                if (
                    "Icon" in file_path_clean and
                    ("\r" in file_path_clean or "\\r" in file_path_clean)
                ):
                    if os.getenv("DAWGIT_DEBUG") == "1":
                        print(f"[DEBUG] Skipping Icon-related file: {repr(file_path_clean)}")
                    continue

                if any(fnmatch.fnmatch(file_path_clean, pat) for pat in excluded_patterns):
                    continue

                print(f"[DEBUG] Detected file change: {file_path_clean}")
                self._last_dirty_state = True
                return True

            # ✅ Treat any changed .als or .logicx file as a reason to allow commit
            for ext in ("*.als", "*.logicx"):
                for daw_file in self.project_path.glob(ext):
                    rel_path = daw_file.relative_to(self.project_path)

                    if daw_file.suffix == ".logicx" and daw_file.is_dir():
                        # 🔍 Look for dirty files inside the .logicx bundle
                        for subfile in daw_file.rglob("*"):
                            sub_rel = subfile.relative_to(self.project_path)
                            if any(sub_rel.as_posix() in line for line in status_output):
                                print(f"[DEBUG] Unsaved LogicX change: {sub_rel}")
                                self._last_dirty_state = True
                                return True
                    else:
                        if any(str(rel_path) in line for line in status_output):
                            print(f"[DEBUG] Unsaved DAW file detected: {rel_path}")
                            self._last_dirty_state = True
                            return True

            # ✅ Only log once when status goes clean
            if getattr(self, "_last_dirty_state", None) is not False:
                print("[DEBUG] has_unsaved_changes() = False")
                self._last_dirty_state = False

            return False

        except Exception as e:
            print(f"[DEBUG] has_unsaved_changes() failed: {e}")
            return False


    def backup_unsaved_changes(self):
        if not self.project_path:
            print("⚠️ No project path defined — skipping backup.")
            return

        try:
            project_path = Path(self.project_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = project_path.parent / f"Backup_{project_path.name}_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)

            for file in project_path.glob("*.*"):
                if file.is_file():
                    shutil.copy(file, backup_dir / file.name)

            print(f"🔒 Unsaved changes backed up to: {backup_dir}")
            return backup_dir
        except Exception as e:
            print(f"[ERROR] Failed to back up unsaved changes: {e}")
            return None


    def get_current_take_name(self):
        try:
            return f"version {sum(1 for _ in self.repo.iter_commits(self.repo.active_branch.name))}"
        except Exception:
            return "(unknown)"
        

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


    def _launch_editable_version_in_daw(self):
        if not self.editable_checkout_path:
            print("[WARN] No editable path to launch.")
            return

        is_fresh_snapshot = str(self.editable_checkout_path).startswith(
            str(Path(self.project_path) / ".dawgit_checkout_work")
        )

        if os.getenv("DAWGIT_TEST_MODE") == "1" or is_fresh_snapshot:
            print("[AUTO] Launching fresh editable snapshot without modal.")
            subprocess.Popen(["open", str(self.editable_checkout_path)])
            return

        # Otherwise, warn user
        confirm = QMessageBox.question(
            self,
            ABLETON_MAY_BE_OPEN_TITLE,
            ABLETON_MAY_BE_OPEN_MSG,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                subprocess.Popen(["open", str(self.editable_checkout_path)])
                print(f"[DEBUG] Opened editable snapshot in DAW: {self.editable_checkout_path}")
            except Exception as e:
                print(f"[ERROR] Failed to open DAW file: {e}")
                self._show_error(f"❌ Could not launch Ableton:\n{e}")



        
    def load_commit_history(self, limit=20, offset=0):
        if not self.repo:
            print("❌ No Git repo loaded.")
            return

        if not self.repo.head.is_valid():
            print("⚠️ Repo exists but has no commits yet.")
            return

        print(f"[DEBUG] Repo valid: {self.repo.head.is_valid()}")
        print(f"[DEBUG] HEAD SHA: {self.repo.head.commit.hexsha}")
        print(f"[DEBUG] Total commits: {self.repo.git.rev_list('--count', 'HEAD')}")

        # Ensure project_path is set
        if not self.project_path:
            self.project_path = Path(tempfile.mkdtemp())
            print(f"[INFO] No project path set, using temporary path: {self.project_path}")

        if not self.repo:
            print("❌ No Git repo loaded.")
            return

        self.load_commit_roles()  # Load commit roles first

        # Show loading message on UI
        if hasattr(self, "status_label"):
            self.snapshot_page.status_label.setText(SNAPSHOT_HISTORY_LOADING)
            QApplication.processEvents()  # Refresh UI immediately

        # Handle empty repo case
        if not self.repo.head.is_valid():
            print("⚠️ Repo exists but has no commits yet.")
            self.snapshot_page.clear_table()
            self.snapshot_page.commit_table.insertRow(0)
            placeholders = ["–", "–", "No commits yet", "–", "–", "–", "–", "–", "–"]
            for col, text in enumerate(placeholders):
                self.snapshot_page.commit_table.setItem(0, col, QTableWidgetItem(text))
            if hasattr(self, "status_label"):
                self.snapshot_page.status_label.setText(SNAPSHOT_HISTORY_LOADED)
            self.update_status_label()
            self.update_role_buttons()
            return

        # Clear table only on initial load (offset=0)
        if offset == 0:
            self.snapshot_page.clear_table()
            # Make sure to clear rows, no redundant clear calls needed
            # self.snapshot_page.commit_table.setRowCount(0)  # redundant if clear_table clears rows

            self.snapshot_page.commit_table.clearSelection()

        head_sha = self.repo.head.commit.hexsha

        try:
            current_branch = self.repo.active_branch.name
        except TypeError:
            current_branch = "(detached HEAD)"

        commit_table = self.snapshot_page.commit_table
        commit_table.setRowCount(0)  # Clear rows on initial load (optional if clear_table does this)

        commits = list(self.repo.iter_commits("HEAD", max_count=limit, skip=offset))
        total_commits = int(self.repo.git.rev_list('--count', 'HEAD').strip())
        self.total_commits = total_commits

        for idx, commit in enumerate(commits):
            row = commit_table.rowCount()
            commit_table.insertRow(row)

            sha_short = commit.hexsha[:7]
            short_msg = commit.message.strip().split("\n")[0]
            date_str = datetime.fromtimestamp(commit.committed_date).strftime("%b %d, %H:%M")

            files_in_commit = commit.tree.traverse()
            file_list = [item.path for item in files_in_commit if item.type == 'blob']
            file_count = str(len(file_list))
            daw_type = "Ableton" if any(".als" in f for f in file_list) else "Logic" if any(".logicx" in f for f in file_list) else "Unknown"
            
            role = self.commit_roles.get(commit.hexsha, "")

            # Commit number — read-only
            index_num = total_commits - (offset + idx)
            item0 = NumericItem(index_num)
            item0.setFlags(item0.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 0, item0)

            # Role — read-only
            item1 = QTableWidgetItem(self.pretty_role(role))
            item1.setFlags(item1.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 1, item1)

            # Commit ID — read-only with tooltip
            item2 = QTableWidgetItem(sha_short)
            item2.setToolTip(commit.hexsha)
            item2.setFlags(item2.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 2, item2)

            # Commit message — editable
            item3 = QTableWidgetItem(short_msg)
            item3.setFlags(item3.flags() | Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 3, item3)

            # Branch names — read-only
            try:
                result = subprocess.run(
                    ["git", "branch", "--contains", commit.hexsha],
                    cwd=self.project_path,
                    env=self.custom_env(),
                    capture_output=True,
                    text=True
                )
                branches = [line.strip().lstrip("* ").strip() for line in result.stdout.strip().splitlines()]
                if current_branch in branches:
                    branches = [f"🎯 MAIN" if b == "main" and b == current_branch
                                else "MAIN" if b == "main"
                                else f"🎯 {b}" if b == current_branch
                                else b
                                for b in branches]
                # branch_str = ", ".join(branches)
                if "main" in branches:
                    branch_str = "MAIN"
                else:
                    branch_str = branches[0]
            except Exception as e:
                print(f"[ERROR] Failed to get branches for {sha_short}: {e}")
                branch_str = "–"
            item4 = QTableWidgetItem(branch_str)
            item4.setFlags(item4.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 4, item4)

            # DAW type — read-only
            item5 = QTableWidgetItem(daw_type)
            item5.setFlags(item5.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 5, item5)

            # File count — read-only
            item6 = QTableWidgetItem(file_count)
            item6.setFlags(item6.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 6, item6)

            # Tags — editable
            tag = self.get_tag_for_commit(commit.hexsha) or ""
            item7 = QTableWidgetItem(tag)
            item7.setFlags(item7.flags() | Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 7, item7)

            # Date — read-only
            item8 = QTableWidgetItem(date_str)
            item8.setFlags(item8.flags() & ~Qt.ItemFlag.ItemIsEditable)
            commit_table.setItem(row, 8, item8)

        commit_table.setSortingEnabled(True)

        # Move highlight outside the loop for performance
        self.snapshot_page.highlight_row_by_sha(head_sha)

        # Sort table so newest commit is first
        commit_table.sortItems(0, Qt.SortOrder.DescendingOrder)

        # Set current commit id from selected row
        self._set_commit_id_from_selected_row()
        if not self.current_commit_id:
            item = commit_table.item(commit_table.currentRow(), 2)
            if item:
                self.current_commit_id = item.toolTip()

        self.update_status_label()
        self.update_role_buttons()

        # Scroll to selected row (usually HEAD)
        head_row = commit_table.currentRow()
        if head_row >= 0:
            commit_table.scrollToItem(
                commit_table.item(head_row, 1),
                QTableWidget.ScrollHint.PositionAtCenter
            )

        # Lazy-load scroll handler — only connect once
        if not hasattr(self, 'commit_history_loaded'):
            self.commit_history_loaded = offset + limit
            commit_table.verticalScrollBar().valueChanged.connect(self.handle_commit_scroll)
        
        
    # Lazy-load scroll handler helper
    def handle_commit_scroll(self):
        scroll_bar = self.snapshot_page.commit_table.verticalScrollBar()
        max_scroll = scroll_bar.maximum()
        current_val = scroll_bar.value()

        if current_val == max_scroll:  # User scrolled to bottom
            if hasattr(self, 'commit_history_loaded') and hasattr(self, 'total_commits'):
                if self.commit_history_loaded >= self.total_commits:
                    # All commits loaded, no more to load
                    return
                else:
                    # Load next batch of commits starting from last offset
                    self.load_commit_history(limit=20, offset=self.commit_history_loaded)
                    self.commit_history_loaded += 20  # Increment after successful load


    def set_commit_id_from_head(self):
        """
        Sets current_commit_id to the current HEAD commit.
        Used after switching branches or restoring project state.
        """
        if self.repo:
            self.current_commit_id = self.repo.head.commit.hexsha
            print(f"[DEBUG] current_commit_id updated to HEAD: {self.current_commit_id}")


    def highlight_current_commit(self):
        try:
            current_commit = self.repo.head.commit.hexsha[:7]
            self.current_commit_id = self.repo.head.commit.hexsha
            self.load_commit_history()


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


    def highlight_and_scroll_to_head(self):
        if not self.repo or not self.snapshot_page.commit_table:
            return

        head_sha = self.repo.head.commit.hexsha
        print(f"[DEBUG] Seeking to highlight SHA: {head_sha[:7]}")

        # Clear highlights
        for r in range(self.snapshot_page.commit_table.rowCount()):
            for c in range(self.snapshot_page.commit_table.columnCount()):
                cell = self.snapshot_page.commit_table.item(r, c)
                if cell:
                    cell.setBackground(Qt.GlobalColor.white)

        for row in range(self.snapshot_page.commit_table.rowCount()):
            item = self.snapshot_page.commit_table.item(row, 1)
            if item and item.toolTip() == head_sha:
                self.snapshot_page.commit_table.selectRow(row)

                # ✅ Add temp spacer row if last row is visible
                if self.snapshot_page.commit_table.rowCount() < 10:  # Tune threshold
                    self.snapshot_page.commit_table.insertRow(self.snapshot_page.commit_table.rowCount())
                    for c in range(self.snapshot_page.commit_table.columnCount()):
                        self.snapshot_page.commit_table.setItem(self.snapshot_page.commit_table.rowCount()-1, c, QTableWidgetItem(""))

                QTimer.singleShot(150, lambda r=row: (
                    self.snapshot_page.commit_table.setCurrentCell(r, 1),
                    self.snapshot_page.commit_table.scrollToItem(self.snapshot_page.commit_table.item(r, 1), QTableWidget.ScrollHint.PositionAtCenter),
                    print(f"[DEBUG] ✅ Forced scroll to row {r}"),
                ))

                for col in range(self.snapshot_page.commit_table.columnCount()):
                    cell = self.snapshot_page.commit_table.item(row, col)
                    if cell:
                        cell.setBackground(Qt.GlobalColor.green)

                self.selected_head_row = row
                break


    def clear_highlight_on_click(self):
        self.current_commit_id = None


    def start_new_version_line(self):
        raw_input, ok = QInputDialog.getText(
            self,
            START_NEW_VERSION_BTN,
            "Name your new version line (e.g. 'alt_take2', 'live_mix', or 'idea_bounce'):\n\n"
            "✅ Use letters, numbers, dashes, or underscores.\n"
            "🚫 Avoid spaces, slashes, or special characters."
        )

        if ok:
            # ✅ Normalize
            branch_name = raw_input.strip().lower().replace(" ", "_")

            # ✅ Sanitize using strict regex
            if not re.match(r"^[a-z0-9_-]+$", branch_name):
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

                # ✅ Refresh UI state
                self.load_commit_history()
                self.update_status_label()
                self.update_role_buttons()

                if hasattr(self, "branch_page"):
                    QTimer.singleShot(300, self.branch_page.populate_branches)

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



    def safe_single_shot(self, delay_ms, callback, parent=None):    
        """
        Schedule a delayed callback using QTimer.singleShot with safety.
        Prevents crash if parent is deleted before the timer fires.
        """
        if parent and not parent.isVisible():
            print("[DEBUG] Skipping QTimer.singleShot — parent not visible.")
            return

        try:
            QTimer.singleShot(delay_ms, callback)
        except Exception as e:
            print(f"[DEBUG] QTimer.singleShot failed: {e}")


    def switch_branch(self, branch_name=None):
        if not self.repo:
            QMessageBox.warning(self, NO_REPO_TITLE, NO_REPO_MSG)
            return {"status": "error", "message": "No repo loaded."}

        try:
            branches = [head.name for head in self.repo.heads]

            if self.has_unsaved_changes():
                self.backup_unsaved_changes()
            
            from daw_git_core import backup_latest_commit_state
            backup_latest_commit_state(self.repo, Path(self.project_path))

            if not branches:
                QMessageBox.information(
                    self,
                    "No Saved Versions",
                    "🎚️ This project has no saved version lines yet.\n\nUse 'Start New Version Line' to begin branching."
                )
                return {"status": "error", "message": "No branches available."}

            if self.repo.head.is_detached:
                choice = QMessageBox.question(
                    self,
                    SNAPSHOT_SWITCH_WARNING_TITLE,
                    SNAPSHOT_SWITCH_WARNING_MSG,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
                )
                if choice != QMessageBox.StandardButton.Yes:
                    return {"status": "cancelled", "message": "User cancelled branch switch from detached HEAD."}

            if not branch_name:
                selected_branch, ok = QInputDialog.getItem(
                    self,
                    "🔀 Switch to Saved Version",
                    "Choose a saved version line:",
                    branches,
                    editable=False
                )
                if not ok or not selected_branch:
                    return {"status": "cancelled", "message": BRANCH_NO_SELECTION}
            else:
                selected_branch = branch_name

            # Perform the actual switch
            result = self.git.switch_branch(selected_branch)

            if result["status"] == "error":
                QMessageBox.critical(self, COULDNT_SWITCH_TITLE, f"❌ Git error:\n\n{result['message']}")
                return result

            if result["status"] == "detached":
                QMessageBox.warning(self, DETACHED_HEAD_TITLE, DETACHED_HEAD_MSG)
                return result

            if result["status"] == "noop":
                QMessageBox.information(self, ALREADY_ON_BRANCH_TITLE, ALREADY_ON_BRANCH_MSG.format(branch=selected_branch))

                return {"status": "success", "message": result["message"]}
            
            # Refresh UI state
            self.repo = self.git.repo  # rebind
            self.init_git()
            if hasattr(self, "load_commit_history"):
                self.load_commit_history()
            if hasattr(self, "update_session_branch_display"):
                self.update_session_branch_display()
            if hasattr(self, "update_version_line_label"):
                self.update_version_line_label()

            QMessageBox.information(
                self,
                "Switched Version",
                f"🎚️ You’re now working on version line:\n\n{selected_branch}"
            )

            if hasattr(self, "commit_page"):
                is_detached = self.repo.head.is_detached
                in_editable = ".dawgit_checkout_work" in str(self.project_path)
                if is_detached and not in_editable:
                    self.commit_page.set_commit_controls_enabled(False, SNAPSHOT_EDIT_BLOCK_TOOLTIP)
                else:
                    self.commit_page.set_commit_controls_enabled(True, "")

            return {"status": "success", "message": f"Switched to branch {selected_branch}"}

        except Exception as e:
            QMessageBox.critical(self, UNEXPECTED_ISSUE_TITLE, f"⚠️ Something unexpected happened:\n\n{e}")
            return {"status": "error", "message": str(e)}



    def open_project_folder(self, event):
        if self.project_path.exists():
            subprocess.run(["open", str(self.project_path)])


    def clear_saved_project(self):
        if self.settings_path.exists():
            try:
                self.settings_path.unlink()
                self.project_path = None  # ✅ clear in memory
                self.update_project_label()  # ✅ update the UI and test state
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


    def update_project_label(self):
        if self.project_path:
            display = f"Tracking: {self.project_path}"
        else:
            display = "🔍 No project loaded"

        if hasattr(self, "project_label"):
            self.project_label.setText(display)

        if hasattr(self, "path_label"):
            self.path_label.setText(str(self.project_path) if self.project_path else "")


    def status_message(self, message):
        print(f"[STATUS] {message}")


    def custom_env(self):
        env = os.environ.copy()
        env["PATH"] = self.env_path
        return env


    def restore_last_backup(self):
        backups = sorted(Path(self.project_path.parent).glob(f"Backup_{self.project_path.name}_*"), reverse=True)
        if not backups:
            QMessageBox.warning(self, NO_BACKUP_FOUND_TITLE, "There are no backup folders for this project.")
            return

        latest_backup = backups[0]
        for file in latest_backup.glob("*.*"):
            if file.is_file():
                shutil.copy(file, self.project_path / file.name)
        QMessageBox.information(self, BACKUP_RESTORED_TITLE, BACKUP_RESTORED_MSG.format(path=latest_backup))



    def timerEvent(self, event):
        if isinstance(self.project_path, str):
            self.project_path = Path(self.project_path)
        if not self.repo or not self.project_path or not self.project_path.exists():
            return  # 🛑 prevent crash if repo or folder is missing (e.g. during tests)

        try:
            has_changes = self.repo.is_dirty(index=True, working_tree=True, untracked_files=True)
        except Exception as e:
            print(f"[WARNING] Skipping is_dirty check — repo error: {e}")
            return

        # 🎚️ Flash toggle flag
        self.unsaved_flash = getattr(self, "unsaved_flash", False)

        if has_changes:
            self.unsaved_flash = not self.unsaved_flash
        else:
            self.unsaved_flash = False


        # ✅ Update alert property and force visual refresh
        if hasattr(self, "unsaved_indicator") and self.unsaved_indicator:
            new_alert = self.unsaved_flash
            self.unsaved_indicator.setProperty("alert", new_alert)

            # Force full restyle
            self.unsaved_indicator.style().unpolish(self.unsaved_indicator)
            self.unsaved_indicator.style().polish(self.unsaved_indicator)
            self.unsaved_indicator.update()

            # Ensure visibility toggles with flash
            self.unsaved_indicator.setVisible(has_changes or self.unsaved_flash)

        # 💾 Legacy "Save Snapshot" button
        if hasattr(self, "commit_btn") and self.commit_btn:
            self.commit_btn.setEnabled(has_changes)
            self.commit_btn.setToolTip(
                "Save a snapshot of your current track state." if has_changes else
                "No new changes — nothing to snapshot yet."
            )

        # 🧠 Auto-snapshot toggle
        if hasattr(self, "auto_save_toggle") and self.auto_save_toggle:
            self.auto_save_toggle.setEnabled(False)
            self.auto_save_toggle.setEnabled(has_changes)
            self.auto_save_toggle.setToolTip(
                "Auto-snapshot is ready — changes detected in your session." if has_changes else
                "✅ All changes saved. Auto-snapshot will resume on next tweak."
            )

        # 🧱 New Commit button
        if hasattr(self, "commit_button") and self.commit_button:
            self.commit_button.setEnabled(has_changes)
            self.commit_button.setToolTip(
                "Lock in this version of your project — save it to your version history." if has_changes else
                "🎵 No tweaks yet — this version matches the last saved snapshot."
            )


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
    

    def update_log(self):
        if not hasattr(self, "history_table"):
            print("[DEBUG] Skipping update_log(): no history_table in test mode.")
            return
        """Legacy compatibility method used in tests — safely redirects to commit history update."""
        self.load_commit_history()
        

    def update_status_label(self):
        if not hasattr(self, "status_label"):
            return

        if not self.repo:
            self.snapshot_page.status_label.setText(NO_REPO_MSG)
            print("[DEBUG] status label set: ❌ No Git repo loaded.")
            return

        try:
            if self.repo.head.is_detached:
                self.snapshot_page.status_label.setText(SNAPSHOT_LOAD_SUCCESS)
                print("[DEBUG] status label set: ℹ️ Detached snapshot — not on an active version line")

            else:
                try:
                    branch = self.repo.active_branch.name
                    commit_count = sum(1 for _ in self.repo.iter_commits(branch))
                except Exception as e:
                    print(f"[DEBUG] update_status_label: failed to read repo state: {e}")
                    return

                # ✅ Test-safe version of the status label
                if os.getenv("DAWGIT_TEST_MODE") == "1":
                    label_text = STATUS_BRANCH_TAKE.format(
                        branch=self.normalize_branch_name(branch), 
                        take=commit_count
                    )
                else:
                    label_text = STATUS_SESSION_LABEL.format(
                        branch=self.normalize_branch_name(branch),
                        version=commit_count
                    )
                self.snapshot_page.status_label.setText(label_text)
                print(f"[DEBUG] status label set: {label_text}")

            # ✅ Show/hide and enable/disable role buttons based on HEAD state
            if hasattr(self, "commit_page"):
                for attr in [
                    "tag_main_btn",
                    "tag_creative_btn",
                    "tag_alt_btn",
                    "tag_custom_btn"
                ]:
                    btn = getattr(self.commit_page, attr, None)
                    if btn:
                        btn.setEnabled(not self.repo.head.is_detached)
                        btn.setToolTip(
                            "❌ Tagging is only available on active version lines."
                            if self.repo.head.is_detached else ""
                        )
                        if self.repo.head.is_detached:
                            btn.hide()
                        else:
                            btn.show()

        except Exception as e:
            self.snapshot_page.status_label.setText(f"⚠️ Git status error: {e}")
            print(f"[DEBUG] status label set: ⚠️ Git status error: {e}")




    def toggle_tooltips(self):
        """Enable or disable tooltips for all interactive elements."""
        enabled = self.show_tooltips_checkbox.isChecked()
        self.settings.setValue("show_tooltips", enabled)

        for widget, tip in self.tooltips.items():
            widget.setToolTip(tip if enabled else "")


    def save_last_project_path(self):
        if not self.project_path or str(self.project_path) == "None":
            print("⚠️ Not saving — project_path is None.")
            return

        app_root = Path(__file__).resolve().parent
        if Path(self.project_path).resolve() == app_root:
            print("⚠️ Refusing to save DAWGitApp folder as last project.")
            return

        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump({"last_project_path": str(self.project_path)}, f)
            print(f"✅ Saved last project path: {self.project_path}")
        except Exception as e:
            print(f"⚠️ Failed to save project path: {e}")


    def get_active_daw_file(self):
        """
        Return the path to the active DAW file (.als or .logicx) if one exists in the project.
        """
        if not self.project_path or not self.project_path.exists():
            return None

        # Check for .als first (Ableton)
        als_files = list(self.project_path.glob("*.als"))
        if als_files:
            return als_files[0]

        # Then check for Logic Pro
        logicx_files = list(self.project_path.glob("*.logicx"))
        if logicx_files:
            return logicx_files[0]

        return None


    def load_project_folder(self, folder_path):
        print(f"[DEBUG] Loading project folder: {folder_path}")
        self.project_path = Path(folder_path)
        os.chdir(self.project_path)
        self.init_git()
        self.save_last_project_path()
        self.load_commit_history()

        # ✅ Sync UI labels
        self.update_session_branch_display()
        self.update_version_line_label()

        # ✅ Ensure "Open in DAW" button is available if file exists
        if self.get_active_daw_file():
            self.open_in_daw_btn.setVisible(True)
            self.open_in_daw_btn.setEnabled(True)
            print("[DEBUG] 🎧 Open DAW button enabled on project load")
        else:
            self.open_in_daw_btn.setVisible(False)
            self.open_in_daw_btn.setEnabled(False)
            print("[DEBUG] ❌ No .als or .logicx file found — button disabled")


    def try_restore_last_project(self):
        if not self.settings_path.exists():
            return

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                last_path = config.get("last_project_path")

            if last_path and Path(last_path).exists() and Path(last_path, ".git").exists():
                print(f"🔁 Restoring last project: {last_path}")
                self.load_project_folder(last_path)
            else:
                print("⚠️ Last project path invalid or no .git folder.")
        except Exception as e:
            print(f"⚠️ Failed to restore last project: {e}")


    def select_folder_clicked(self):
        if self.project_path and Path(self.project_path, ".git").exists():
            QMessageBox.information(
                self,
                "Project Already Loaded",
                f"🎶 You’re already working in:\n{self.project_path}"
            )
            return

        selected = QFileDialog.getExistingDirectory(self, "Select DAW Project Folder")
        if selected:
            self.load_project(selected)


    def is_valid_daw_folder(self, path):
        return any(path.glob("*.als")) or any(path.glob("*.logicx"))        

    
    def load_saved_project_path(self):
        # Check if the settings file exists
        if not self.settings_path.exists():
            print("⚠️ No saved project path found.")
            return None
        

        # ✅ Print the path being used (For Testing Only)
        # print(f"[DEBUG] Settings path = {self.settings_path}")

        try:
            # Attempt to read the saved project path from the settings file
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_path = data.get("last_project_path", "")
                print(f"[DEBUG] Loaded last_path from file: {last_path}")
            # ✅ Skip leftover test paths
            if "pytest-" in str(last_path):
                print("⚠️ Skipping test repo path.")
                return None
        except Exception as e:
            print(f"⚠️ Failed to load saved project path: {e}")
            return None

        # If no saved path exists, return None
        if not last_path:
            return None

        # Resolve the path to its absolute form
        resolved_path = Path(last_path).resolve()

        # 🛑 Block DAWGitApp root folder from being set as a project
        app_root = Path(__file__).resolve().parent
        if resolved_path == app_root or "DAWGitApp" in str(resolved_path):
            print("⚠️ Refusing to track DAWGitApp root folder — not a valid project.")
            return None

        # Check if the folder at the resolved path exists
        if not resolved_path.exists():
            print("⚠️ Last path no longer exists.")
            return None

        # Ensure that there is at least one DAW file in the folder (.als or .logicx)
        daw_files = list(resolved_path.glob("*.als")) + list(resolved_path.glob("*.logicx"))
        if not daw_files and not os.getenv("DAWGIT_TEST_MODE"):
            print("⚠️ No DAW file found in saved folder.")
            return None

        # Return the resolved path if everything is valid
        print(f"✅ Loaded saved project path: {resolved_path}")
        return str(resolved_path)



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


    def show_status_message(self, message=None, timeout=3000):
        """🎵 Display a status message to the user in the status label and status bar."""
        
        if message is None:
            message = STATUS_UNKNOWN

        # ✅ Show in macOS-style status bar (optional)
        self.statusBar().showMessage(message, timeout)

        # ✅ Set direct message to UI label — no "Status:" prefix
        if hasattr(self, 'status_label'):
            self.snapshot_page.status_label.setText(message)
        else:
            print(f"[STATUS] {message}")
            

    def _show_info(self, message):
        QMessageBox.information(self, HEADS_UP_TITLE, message)


    def _show_warning(self, message):
        QMessageBox.warning(self, HEADS_UP_TITLE, message)


    def _show_error(self, message):
        QMessageBox.critical(self, SESSION_SETUP_FAILED_MSG, message)



# Handle Ctrl+C gracefully
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DAWGitApp()
    win.show()
    sys.exit(app.exec())

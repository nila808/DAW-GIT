from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

from ui_strings import (
    BRANCH_MANAGER_TITLE,
    SWITCH_BRANCH_BTN,
    START_NEW_VERSION_BTN,
    NO_REPO_LOADED_MSG, 
    SESSION_LINES_LOADED_MSG
)

class BranchManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent  # 💈 Link to DAWGitApp
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel(BRANCH_MANAGER_TITLE)
        layout.addWidget(self.title_label)

        # Branch dropdown
        # self.branch_dropdown = QComboBox()
        # display_name = "MAIN" if branch.name == "main" else branch.name
        self.branch_dropdown = QComboBox()
        layout.addWidget(self.branch_dropdown)

        # Buttons
        actions = QHBoxLayout()
        self.switch_branch_btn = QPushButton(SWITCH_BRANCH_BTN)
        self.start_new_branch_btn = QPushButton(START_NEW_VERSION_BTN)
        actions.addWidget(self.switch_branch_btn)
        actions.addWidget(self.start_new_branch_btn)
        layout.addLayout(actions)

        self.switch_branch_btn.clicked.connect(self.switch_selected_branch)
        self.start_new_branch_btn.clicked.connect(self.app.start_new_version_line)

        # Status label
        self.status_label = QLabel("\ud83d\udccd No branch selected")
        layout.addWidget(self.status_label)


    def populate_branches(self):
        if not self.app or not self.app.repo:
            self.status_label.setText(NO_REPO_LOADED_MSG)
            if hasattr(self, "snapshot_status"):
                self.snapshot_status.setText(NO_REPO_LOADED_MSG)  # Set UX status based on context
            return

        branches = [head.name for head in self.app.repo.heads]
        display_branches = ["MAIN" if b == "main" else b for b in branches]

        self.branch_dropdown.clear()
        self.branch_dropdown.addItems(display_branches)

        try:
            current_branch = self.app.repo.active_branch.name
            display_branch = "MAIN" if current_branch == "main" else current_branch
            index = display_branches.index(display_branch)
            self.branch_dropdown.setCurrentIndex(index)
        except Exception:
            self.branch_dropdown.setCurrentIndex(-1)

        self.status_label.setText(SESSION_LINES_LOADED_MSG.format(count=len(branches)))
        if hasattr(self, "snapshot_status"):
            self.snapshot_status.setText(SESSION_LINES_LOADED_MSG)  # Set UX status based on context

        

    def switch_selected_branch(self):
        branch_name = self.branch_dropdown.currentText()
        if branch_name:
            result = self.app.switch_branch(branch_name)

            msg = result.get("message", "Branch switched.") if isinstance(result, dict) else str(result)
            self.status_label.setText(msg)

            # ✅ Update snapshot_status with session-aware UX message
            if hasattr(self, "snapshot_status"):
                if result.get("status") == "success":
                    self.snapshot_status.setText(f"🎼 Editing: version on '{branch_name}'")
                else:
                    self.snapshot_status.setText("⚠️ Couldn't switch branch.")

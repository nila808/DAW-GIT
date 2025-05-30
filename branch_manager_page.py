# branch_manager_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from ui_strings import (
    BRANCH_MANAGER_TITLE,
    SWITCH_BRANCH_BUTTON,
    START_VERSION_LINE_BUTTON,
    NO_REPO_LOADED_LABEL,
    BRANCHES_LOADED_LABEL,
)

class BranchManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent  # 👈 Link to DAWGitApp
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel(BRANCH_MANAGER_TITLE)
        layout.addWidget(self.title_label)

        # Branch dropdown
        self.branch_dropdown = QComboBox()
        layout.addWidget(self.branch_dropdown)

        # Buttons
        actions = QHBoxLayout()
        self.switch_branch_btn = QPushButton(SWITCH_BRANCH_BUTTON)
        self.start_new_branch_btn = QPushButton(START_VERSION_LINE_BUTTON)
        actions.addWidget(self.switch_branch_btn)
        actions.addWidget(self.start_new_branch_btn)
        layout.addLayout(actions)

        self.switch_branch_btn.clicked.connect(self.switch_selected_branch)
        self.start_new_branch_btn.clicked.connect(self.app.start_new_version_line)

        # Status label
        self.status_label = QLabel(NO_REPO_LOADED_LABEL)
        layout.addWidget(self.status_label)

    def populate_branches(self):
        if not self.app or not self.app.repo:
            self.status_label.setText(NO_REPO_LOADED_LABEL)
            return

        branches = [head.name for head in self.app.repo.heads]
        self.branch_dropdown.clear()
        self.branch_dropdown.addItems(branches)

        # Select the current branch in the dropdown
        try:
            current_branch = self.app.repo.active_branch.name
            index = branches.index(current_branch)
            self.branch_dropdown.setCurrentIndex(index)
        except Exception:
            self.branch_dropdown.setCurrentIndex(-1)

        self.status_label.setText(BRANCHES_LOADED_LABEL.format(count=len(branches)))

    def switch_selected_branch(self):
        branch_name = self.branch_dropdown.currentText()
        if branch_name:
            result = self.app.switch_branch(branch_name)
            msg = result.get("message", "Branch switched.") if isinstance(result, dict) else str(result)
            self.status_label.setText(msg)

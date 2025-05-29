from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

class BranchManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent  # 👈 Link to DAWGitApp
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("🌳 Branch Manager")
        layout.addWidget(self.title_label)

        # Branch dropdown
        self.branch_dropdown = QComboBox()
        layout.addWidget(self.branch_dropdown)

        # Buttons
        actions = QHBoxLayout()
        self.switch_branch_btn = QPushButton("🔀 Switch Branch")
        self.start_new_branch_btn = QPushButton("🎼 Start New Version Line")
        actions.addWidget(self.switch_branch_btn)
        actions.addWidget(self.start_new_branch_btn)
        layout.addLayout(actions)

        self.switch_branch_btn.clicked.connect(self.switch_selected_branch)
        self.start_new_branch_btn.clicked.connect(self.app.start_new_version_line)

        # Status label
        self.status_label = QLabel("📍 No branch selected")
        layout.addWidget(self.status_label)

        # self.populate_branches()  # 👈 Load the dropdown on init


    def populate_branches(self):
        if not self.app or not self.app.repo:
            self.status_label.setText("⚠️ No Git repo loaded.")
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
            # If in detached HEAD or branch not found, select none
            self.branch_dropdown.setCurrentIndex(-1)

        self.status_label.setText(f"✅ {len(branches)} branches loaded.")



    def switch_selected_branch(self):
        branch_name = self.branch_dropdown.currentText()
        if branch_name:
            result = self.app.switch_branch(branch_name)
            msg = result.get("message", "Branch switched.") if isinstance(result, dict) else str(result)
            self.status_label.setText(msg)

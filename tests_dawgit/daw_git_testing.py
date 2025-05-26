# daw_git_testing.py

import os
from PyQt6.QtWidgets import QMessageBox, QInputDialog

if os.getenv("DAWGIT_TEST_MODE") == "1":
    print("[TEST MODE] 🛡️ Auto-patching modals")
    QMessageBox.question = lambda *a, **kw: QMessageBox.StandardButton.Yes
    QMessageBox.information = lambda *a, **kw: None
    QMessageBox.warning = lambda *a, **kw: None
    QMessageBox.critical = lambda *a, **kw: None
    QInputDialog.getText = lambda *a, **kw: ("test_branch_input", True)
    QInputDialog.getItem = lambda *a, **kw: ("main", True)

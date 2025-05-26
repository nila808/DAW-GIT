import os
os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # patches modals at import
import pytest
from PyQt6.QtWidgets import QTableWidgetItem

def test_return_to_latest_scrolls_to_head_commit(qtbot, app):
    """
    AT-067 / MT-054 — Returning to latest should scroll and select HEAD commit in the table.
    """

    # Simulate detached HEAD by checking out an old commit
    old_commit = app.repo.git.rev_list("--max-parents=0", "HEAD").splitlines()[0]
    app.checkout_selected_commit(commit_sha=old_commit)

    # Confirm detached
    assert app.repo.head.is_detached
    assert "detached" in app.status_label.text().lower()

    # Click 'Return to Latest'
    app.return_to_latest_clicked()

    # Check state updated correctly
    assert not app.repo.head.is_detached
    head_sha = app.repo.head.commit.hexsha[:7]

    # Look for selected row
    selected_row = app.history_table.currentRow()
    item = app.history_table.item(selected_row, 1)
    assert item and head_sha in item.text(), f"Expected HEAD {head_sha} in row {selected_row}, got: {item.text() if item else None}"

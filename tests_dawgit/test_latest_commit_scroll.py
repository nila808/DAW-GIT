import os
os.environ["DAWGIT_TEST_MODE"] = "1"  # ✅ Enable test mode for all patches

import pytest
from pytestqt import qtbot
import daw_git_testing  # ✅ Auto-patch dialogs


def test_return_to_latest_scrolls_to_head_commit(qtbot, app):
    """
    AT-067 / MT-054 — Returning to latest should scroll and select HEAD commit in the table.
    """
    # ✅ Create two commits
    als_file = app.project_path / "track.als"
    als_file.write_text("initial content")
    app.commit_changes("Initial snapshot")

    als_file.write_text("second snapshot")
    app.commit_changes("Second snapshot")

    # ✅ Checkout oldest commit (detached HEAD)
    old_commit = app.repo.git.rev_list("--max-parents=0", "HEAD").splitlines()[0]
    app.checkout_selected_commit(commit_sha=old_commit)

    assert app.repo.head.is_detached
    qtbot.waitUntil(
        lambda: "read-only mode" in app.snapshot_page.status_label.text().lower(),
        timeout=2000
    )

    # ✅ Return to latest
    app.return_to_latest_clicked()
    app.update_log()
    assert not app.repo.head.is_detached

    # ✅ Wait for scroll to complete
    qtbot.wait(300)

    # ✅ Check that selected row matches latest HEAD
    selected_row = app.history_table.currentRow()
    item = app.history_table.item(selected_row, 2)
    short_sha = app.repo.head.commit.hexsha[:7]

    print(f"[DEBUG TEST] Selected row = {selected_row}, tooltip = {item.toolTip() if item else '[None]'}")

    assert item, "No item found in selected row."
    assert item.toolTip(), "No tooltip found in selected row."
    assert short_sha in item.toolTip(), f"Expected short SHA {short_sha} in tooltip: {item.toolTip()}"

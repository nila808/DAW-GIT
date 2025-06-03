import ui_strings
import pytest
import os

os.environ["DAWGIT_TEST_MODE"] = "1"
os.environ["DAWGIT_FORCE_INPUT"] = "1"

from ui_strings import SNAPSHOT_EDIT_BLOCK_TOOLTIP

def test_commit_buttons_disabled_in_snapshot_mode(app_with_repo):
    app = app_with_repo

    # ✅ Add second commit if needed
    if len(list(app.repo.iter_commits("main"))) < 2:
        with open(app.project_path / "second.als", "w") as f:
            f.write("Second version")
        app.repo.git.add(".")
        app.repo.index.commit("Second version take")

    # ✅ Checkout to oldest commit to simulate snapshot
    history = list(app.repo.iter_commits("main"))
    old_commit = history[-1].hexsha
    result = app.checkout_selected_commit(old_commit)

    assert result["status"] == "success"

    # ✅ Check that commit UI is disabled
    assert not app.commit_page.commit_button.isEnabled()
    assert not app.commit_page.tag_main_btn.isEnabled()
    assert not app.commit_page.tag_alt_btn.isEnabled()

    # ✅ Check tooltips
    assert app.commit_page.commit_button.toolTip() == SNAPSHOT_EDIT_BLOCK_TOOLTIP
    assert app.commit_page.tag_main_btn.toolTip() == SNAPSHOT_EDIT_BLOCK_TOOLTIP

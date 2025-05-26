import os
import json
import shutil
import pytest
import uuid
from pathlib import Path
from git import Repo
from daw_git_gui import DAWGitApp

os.environ["DAWGIT_TEST_MODE"] = "1"
import daw_git_testing  # ensures all modals are patched early

@pytest.mark.parametrize("label", ["Main Mix", "creative_take", "alt_mixdown", "my_custom_tag"])
def test_assign_commit_role_variants(monkeypatch, qtbot, label):
    test_path = f"/tmp/test_daw_tagging_{uuid.uuid4().hex}"
    project_path = Path(test_path)
    project_path.mkdir(parents=True, exist_ok=True)
    os.environ["DAWGIT_FORCE_TEST_PATH"] = test_path

    # 📝 Create test .als file
    daw_file = project_path / "session.als"
    daw_file.write_text("init")

    # 🔃 Initialize Git repo
    Repo.init(project_path)
    repo = Repo(project_path)

    # ✅ Safely set working directory during Git add/commit
    try:
        cwd = os.getcwd()
    except FileNotFoundError:
        cwd = "/tmp"

    os.chdir(project_path)
    try:
        repo.index.add([daw_file.name])
        repo.index.commit("Initial commit")
    finally:
        os.chdir(cwd)

    # 🖥 Launch the app
    app = DAWGitApp(build_ui=True)
    qtbot.addWidget(app)
    qtbot.wait(200)

    status = app.status_label.text()
    print(f"[DEBUG] status_label: {status}")
    assert any(term in status for term in [
        "Ready", "Session branch", "Take:", "Detached snapshot"
    ]), f"Unexpected status label: {status}"

    # 🔖 Assign and verify role
    sha = app.repo.head.commit.hexsha
    app.assign_commit_role(sha, label)
    app.save_commit_roles()
    qtbot.wait(100)

    roles_path = project_path / ".dawgit_roles.json"
    assert roles_path.exists()
    roles = json.loads(roles_path.read_text())
    assert roles.get(sha) == label, f"Expected role '{label}' on commit {sha[:7]}"

    # ✅ Safe shutdown and cleanup
    app.close()
    qtbot.wait(100)
    if project_path.exists():
        shutil.rmtree(project_path, ignore_errors=True)

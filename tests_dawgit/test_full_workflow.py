import os
import subprocess
import tempfile
from pathlib import Path
from git import Repo, GitCommandError
import pytest

def test_daw_git_end_to_end():
    # Step 1: Create dummy DAW project folder
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "TestProject"
        project_path.mkdir()

        # Simulate a Logic Pro project folder (.logicx)
        logicx_path = project_path / "MyTrack.logicx"
        logicx_path.mkdir()
        (logicx_path / "ProjectData").write_text("Initial content")

        # Step 2: Initialize Git and LFS with 'main' as initial branch
        repo = Repo.init(project_path, initial_branch="main")
        subprocess.run(["git", "lfs", "install"], cwd=project_path)
        subprocess.run(["git", "lfs", "track", "*.logicx/**"], cwd=project_path)
        (project_path / ".gitattributes").write_text("*.logicx/** filter=lfs diff=lfs merge=lfs -text")

        # Step 3: First commit
        repo.index.add([".gitattributes", "MyTrack.logicx/ProjectData"])
        repo.index.commit("Initial commit: tracking MyTrack.logicx")

        # Confirm we are on 'main'
        try:
            assert repo.active_branch.name == "main"
        except TypeError:
            pytest.fail("Not on a named branch after init")

        # Step 4: Create and switch to new branch
        repo.git.checkout("-b", "version_1")
        (logicx_path / "ProjectData").write_text("Changed on version_1")
        repo.index.add(["MyTrack.logicx/ProjectData"])
        repo.index.commit("Change on version_1 branch")

        # ✅ Commit again to allow safe checkout to main
        (logicx_path / "ProjectData").write_text("Safe commit before switch")
        repo.index.add(["MyTrack.logicx/ProjectData"])
        repo.index.commit("Intermediate commit to allow safe checkout")

        # Step 5: Try to switch back to main safely
        switched = False
        for attempt in range(5):
            try:
                repo.git.add("-u")
                repo.git.commit("-m", f"Pre-checkout autosave {attempt + 1}")
            except GitCommandError:
                pass  # Nothing to commit
            try:
                repo.git.clean("-fd")     # Remove untracked files
                repo.git.reset("--hard")  # Ensure clean working tree
                repo.git.checkout("main")
                switched = True
                break
            except GitCommandError as e:
                print(f"[DEBUG] Checkout failed: {e}\nTrying again...")

        if not switched:
            pytest.fail("Failed to switch back to main after multiple attempts")

        # Step 6: Continue work on main branch
        (logicx_path / "ProjectData").write_text("Update on main branch")
        repo.index.add(["MyTrack.logicx/ProjectData"])
        repo.index.commit("Update on main")

        # Step 7: Create second dummy project to simulate folder switch
        second_project = Path(temp_dir) / "SecondProject"
        second_project.mkdir()
        (second_project / "Song2.als").write_text("Ableton song data")

        repo2 = Repo.init(second_project)
        subprocess.run(["git", "lfs", "track", "*.als"], cwd=second_project)
        (second_project / ".gitattributes").write_text("*.als filter=lfs diff=lfs merge=lfs -text")
        repo2.index.add([".gitattributes", "Song2.als"])
        repo2.index.commit("Initial commit in second project")

        # ✅ Assertions
        assert repo.head.commit.message == "Update on main"
        assert repo.active_branch.name == "main"
        assert "version_1" in [b.name for b in repo.branches]
        assert repo2.head.commit.message == "Initial commit in second project"

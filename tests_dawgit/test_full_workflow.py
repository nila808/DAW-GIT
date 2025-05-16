import os
import subprocess
import tempfile
from pathlib import Path
from git import Repo, GitCommandError
import pytest

def test_daw_git_end_to_end():
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "TestProject"
        project_path.mkdir()

        logicx_path = project_path / "MyTrack.logicx"
        logicx_path.mkdir()
        (logicx_path / "ProjectData").write_text("Initial content")

        # Init repo with 'main' branch explicitly
        repo = Repo.init(project_path, initial_branch="main")

        # Setup Git LFS tracking for .logicx folder/files
        subprocess.run(["git", "lfs", "install"], cwd=project_path, check=True)
        subprocess.run(["git", "lfs", "track", "*.logicx/**"], cwd=project_path, check=True)

        # Write .gitattributes file (merge if needed)
        gitattributes = project_path / ".gitattributes"
        gitattributes.write_text("*.logicx/** filter=lfs diff=lfs merge=lfs -text")

        repo.index.add([str(gitattributes.relative_to(project_path)), "MyTrack.logicx/ProjectData"])
        repo.index.commit("Initial commit: tracking MyTrack.logicx")

        assert repo.active_branch.name == "main"

        # Create and checkout new branch
        repo.git.checkout("-b", "version_1")
        (logicx_path / "ProjectData").write_text("Changed on version_1")
        repo.index.add(["MyTrack.logicx/ProjectData"])
        repo.index.commit("Change on version_1 branch")

        # Commit again on version_1 to allow safe checkout later
        (logicx_path / "ProjectData").write_text("Safe commit before switch")
        repo.index.add(["MyTrack.logicx/ProjectData"])
        repo.index.commit("Intermediate commit to allow safe checkout")

        # Try to switch back to main safely with retries
        switched = False
        for attempt in range(5):
            try:
                repo.git.add("-u")
                repo.git.commit("-m", f"Pre-checkout autosave {attempt + 1}")
            except GitCommandError:
                pass  # no changes to commit

            try:
                repo.git.clean("-fd")     # Remove untracked files
                repo.git.reset("--hard")  # Clean working tree
                repo.git.checkout("main")
                switched = True
                break
            except GitCommandError as e:
                print(f"[DEBUG] Checkout failed attempt {attempt + 1}: {e}")

        if not switched:
            pytest.fail("Failed to switch back to main after multiple attempts")

        # Commit update on main
        (logicx_path / "ProjectData").write_text("Update on main branch")
        repo.index.add(["MyTrack.logicx/ProjectData"])
        repo.index.commit("Update on main")

        # Second dummy Ableton project (.als)
        second_project = Path(temp_dir) / "SecondProject"
        second_project.mkdir()
        (second_project / "Song2.als").write_text("Ableton song data")

        repo2 = Repo.init(second_project)
        subprocess.run(["git", "lfs", "install"], cwd=second_project, check=True)
        subprocess.run(["git", "lfs", "track", "*.als"], cwd=second_project, check=True)
        (second_project / ".gitattributes").write_text("*.als filter=lfs diff=lfs merge=lfs -text")

        repo2.index.add([str((second_project / ".gitattributes").relative_to(second_project)), "Song2.als"])
        repo2.index.commit("Initial commit in second project")

        # Assertions
        assert repo.head.commit.message == "Update on main"
        assert repo.active_branch.name == "main"
        assert "version_1" in [b.name for b in repo.branches]
        assert repo2.head.commit.message == "Initial commit in second project"

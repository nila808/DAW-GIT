from pathlib import Path
import subprocess
import os
import json
from datetime import datetime
from git import Repo, GitCommandError


class GitProjectManager:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.repo = None
        self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]

    def init_repo(self):
        print("[DEBUG] Initializing Git...")

        app_root = Path(__file__).resolve().parent
        if self.project_path.resolve() == app_root:
            print("⚠️ Refusing to track DAWGitApp root folder — not a valid project.")
            return {"status": "invalid", "message": "Cannot track app root folder."}

        if not self.project_path.exists():
            print("❌ Invalid or missing project path. Aborting Git setup.")
            return {"status": "invalid", "message": "Missing or invalid project path."}

        daw_files = list(self.project_path.glob("*.als")) + list(self.project_path.glob("*.logicx"))
        print(f"[DEBUG] Found DAW files: {daw_files}")

        is_test_mode = os.getenv("DAWGIT_TEST_MODE") == "1"
        if not daw_files and not is_test_mode:
            print("⚠️ No .als or .logicx file found in selected folder. Aborting Git setup.")
            return {"status": "invalid", "message": "No DAW files found."}
        elif not daw_files:
            print("🧪 [Test Mode] No DAW files found — continuing with empty project.")

        try:
            if (self.project_path / ".git").exists():
                try:
                    print(f"[DEBUG] Found existing Git repo at {self.project_path}")
                    self.repo = Repo(self.project_path)

                    if self.repo.head.is_detached:
                        print("🎯 Repo is in detached HEAD state — skipping HEAD rebinding.")
                        return {"status": "detached", "message": "Detached HEAD state detected."}

                    if not self.repo.head.is_valid():
                        print("🧪 No commits found — auto-committing initial DAW files...")
                        self.repo.index.add([str(f.relative_to(self.project_path)) for f in daw_files])
                        self.repo.index.commit("Initial commit")

                except InvalidGitRepositoryError:
                    print("❌ Invalid Git repository. Re-initializing repository...")
                    self.repo = None
                    return {"status": "invalid", "message": "Invalid Git repository."}

            else:
                print(f"[DEBUG] No existing repo found. Initializing new repo at {self.project_path}")
                self.repo = Repo.init(self.project_path)

                default_ignores = {
                    ".DS_Store", "PROJECT_MARKER.json", ".dawgit_roles.json",
                    "*.asd", "*.bak", "*.tmp", "*.swp", "Ableton Project Info/*"
                }

                gitignore_path = self.project_path / ".gitignore"
                existing_lines = set()
                if gitignore_path.exists():
                    existing_lines = set(gitignore_path.read_text().splitlines())

                new_lines = sorted(default_ignores - existing_lines)
                if new_lines:
                    with gitignore_path.open("a") as f:
                        for line in new_lines:
                            f.write(f"{line}\n")
                    print("[DEBUG] Appended default ignores to .gitignore")

                print("✅ New Git repo initialized.")
                self.repo.index.add([str(f.relative_to(self.project_path)) for f in daw_files])
                self.repo.index.commit("Initial commit")

        except Exception as e:
            print(f"❌ Failed to initialize Git repo: {e}")
            self.repo = None
            return {"status": "error", "message": str(e)}

        return {"status": "ok"}


    def commit_changes(self, message):
        if not self.repo:
            return {"status": "error", "message": "No Git repo available."}

        if not message or not message.strip():
            return {"status": "error", "message": "Commit message cannot be empty."}

        daw_files = list(self.project_path.glob("*.als")) + list(self.project_path.glob("*.logicx"))
        if not daw_files:
            return {"status": "error", "message": "No DAW file to commit."}

        try:
            self.repo.git.add(A=True)
            self.repo.git.commit("-m", message.strip())
            sha = self.repo.head.commit.hexsha
            return {"status": "success", "sha": sha}
        except GitCommandError as e:
            return {"status": "error", "message": str(e)}
        

    def is_dirty(self):
        return self.repo.is_dirty(index=True, working_tree=True, untracked_files=True)

    def stash_uncommitted_changes(self, message="DAWGit auto-stash"):
        if self.repo.is_dirty(untracked_files=True):
            self.repo.git.stash("save", "--include-untracked", message)
            return True
        return False

    def get_latest_commit_sha(self):
        return self.repo.head.commit.hexsha if self.repo.head.is_valid() else None

    def get_branch_name(self):
        try:
            return self.repo.active_branch.name
        except TypeError:
            return "(detached)"

    def assign_commit_role(self, sha, role):
        meta_file = self.project_path / ".dawgit_roles.json"
        roles = {}
        if meta_file.exists():
            try:
                roles = json.loads(meta_file.read_text())
            except Exception:
                roles = {}
        roles[sha] = role
        meta_file.write_text(json.dumps(roles, indent=2))
        return True

    def get_commit_roles(self):
        meta_file = self.project_path / ".dawgit_roles.json"
        if meta_file.exists():
            try:
                return json.loads(meta_file.read_text())
            except Exception:
                return {}
        return {}

    def custom_env(self):
        env = os.environ.copy()
        env["PATH"] = self.env_path
        return env

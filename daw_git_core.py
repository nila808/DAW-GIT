import os
import json
import subprocess
import shutil
import re
from pathlib import Path
from datetime import datetime
from git import Repo, GitCommandError


def sanitize_git_input(user_input: str, allow_spaces=False):
    """Remove dangerous characters and enforce safe Git naming."""
    user_input = user_input.strip()
    if not allow_spaces:
        user_input = user_input.replace(" ", "-")
    # Only allow safe characters (alphanum, dash, underscore, dot)
    sanitized = re.sub(r"[^a-zA-Z0-9\-_\.]", "", user_input)
    return sanitized


class GitProjectManager:
    def __init__(self, project_path):
        if project_path is None:
            self.project_path = None
            self.repo = None
            self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]
            return  # ✅ Exit early — invalid path

        self.project_path = Path(project_path)
        self.repo = None
        self.env_path = "/usr/local/bin:/opt/homebrew/bin:" + os.environ["PATH"]
        self.init_repo()

    def init_repo(self):
        print("[DEBUG] Initializing Git...")

        app_root = Path(__file__).resolve().parent
        if not self.project_path:
            print("❌ Cannot resolve project path — it's None.")
            return {"status": "invalid", "message": "Missing project path."}

        app_path_resolved = self.project_path.resolve()
        if app_path_resolved == app_root:
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
                        if os.getenv("DAWGIT_TEST_MODE") == "1":
                            print("🧪 [Test Mode] Skipping rebind from detached HEAD")
                        else:
                            print("🎯 Repo is in detached HEAD state — attempting to rebind to 'main'")
                            try:
                                self.repo.git.checkout("main", force=True)
                                self.repo = Repo(self.project_path)
                                print("✅ Successfully rebound to 'main' branch.")
                            except GitCommandError as e:
                                print("❌ Failed to rebind to main:", e)
                                return {"status": "detached", "message": f"Detached HEAD — and failed to rebind: {e}"}


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
            msg = str(e)
            if "nothing to commit" in msg:
                return {"status": "error", "message": "Nothing new to commit — your project hasn't changed."}
            return {"status": "error", "message": msg}
        

    def get_current_branch(self):
        try:
            return self.repo.active_branch.name
        except TypeError:
            # Detached HEAD fallback
            if self.repo.head.is_detached:
                return None
            raise
        except Exception as e:
            print(f"[DEBUG] ❌ Error getting current branch: {e}")
            return None


    def is_detached_head(self):
        try:
            return self.repo.head.is_detached
        except Exception:
            return False


    # These 2 methods are for test_commit_then_switch_branch_then_return (refresh_status and get_branch_name) 
    def refresh_status(self):
        # You can optionally do something more meaningful here
        _ = self.repo.git.status()

    def get_branch_name(self):
        return self.repo.active_branch.name
    
    def is_dirty(self):
        return self.repo.is_dirty(index=True, working_tree=True, untracked_files=True)


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


    def stash_uncommitted_changes(self, message="DAWGit auto-stash"):
        if not self.repo:
            return {"status": "error", "message": "No Git repo available."}

        try:
            if self.repo.is_dirty(untracked_files=True):
                self.repo.git.stash("save", "--include-untracked", message)
                return {"status": "stashed", "message": message}
            else:
                return {"status": "clean", "message": "No changes to stash."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


    def switch_branch(self, target_branch, stash_if_dirty=True):
            if not self.repo:
                return {"status": "error", "message": "No Git repo available."}

            current_branch = None
            try:
                current_branch = self.repo.active_branch.name
            except TypeError:
                return {"status": "detached", "message": "Detached HEAD state."}

            if current_branch == target_branch:
                return {"status": "noop", "message": "Already on target branch."}

            if stash_if_dirty:
                stash_result = self.stash_uncommitted_changes()
                if stash_result["status"] == "error":
                    return {"status": "error", "message": stash_result["message"]}

            try:
                if target_branch not in self.repo.heads:
                    self.repo.git.checkout("-b", target_branch)
                    return {"status": "created", "branch": target_branch}
                else:
                    self.repo.git.checkout(target_branch)
                    return {"status": "switched", "branch": target_branch}
            except GitCommandError as e:
                return {"status": "error", "message": str(e)}
            

    def is_valid_git_tag(tag: str) -> bool:
        """
        Git tag rules:
        - No spaces
        - No control chars
        - Cannot start with "-"
        - Cannot contain "~ ^ : ? * [ \\"
        """
        return (
            bool(tag) and
            not tag.startswith("-") and
            re.match(r"^[A-Za-z0-9._/-]+$", tag)
        )
    

def backup_latest_commit_state(repo, project_path, commit_sha=None):
    """
    🎛️ Snapshot Safety Anchor
    """
    if not repo or not project_path:
        print("[backup] Skipped — no project loaded.")
        return

    latest_commit = commit_sha or repo.head.commit.hexsha
    backup_dir = project_path / ".dawgit_cache" / "latest_snapshot" / latest_commit

    if backup_dir.exists():
        print(f"[backup] Already safe — folder exists for: {latest_commit}")
        return

    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"[backup] Backing up current session to: {backup_dir}")

    for item in project_path.iterdir():
        if item.name.startswith(".dawgit"):
            continue
        dest = backup_dir / item.name
        try:
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy(item, dest)
        except Exception as e:
            print(f"[backup] Failed to copy {item.name}: {e}")


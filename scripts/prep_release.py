#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
root = Path(__file__).resolve().parent.parent
status_path = root / "PROJECT_STATUS.md"
changelog_path = root / "CHANGELOG.md"
log_path = root / "release.log"

# Detect current Git branch
def get_current_branch():
    try:
        result = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
        return result.decode().strip()
    except Exception as e:
        print(f"❌ Failed to get current branch: {e}")
        return "main"

branch = get_current_branch()

# Gather recent commits
def get_recent_commits():
    try:
        result = subprocess.check_output(["git", "log", "-5", "--pretty=format:- %s"], cwd=root)
        return result.decode().strip()
    except Exception as e:
        return "- No recent commits found."

status_updated = False
changelog_updated = False

# 1. Update PROJECT_STATUS.md date
print("🔄 Updating PROJECT_STATUS.md...")
if status_path.exists():
    lines = status_path.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith("_Last updated:"):
            lines[i] = f"_Last updated: {datetime.today().strftime('%Y-%m-%d')}_"
            status_path.write_text("\n".join(lines))
            status_updated = True
            print("✅ Date updated.")
            break
else:
    print("❌ PROJECT_STATUS.md not found.")

# 2. Update CHANGELOG.md with version and commits
version_tag = input("🔖 Enter version tag (e.g. v1.0.3-testpass): ").strip()
author = os.getenv("USER") or os.getenv("USERNAME") or "unknown"
recent_commits = get_recent_commits()
entry = f"\n\n## [{version_tag}] – {datetime.today().strftime('%Y-%m-%d')}\n**Author:** @{author}\n{recent_commits}\n"

print("📝 Appending to CHANGELOG.md...")
if changelog_path.exists():
    with open(changelog_path, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(entry + content)
        changelog_updated = True
        print("✅ CHANGELOG.md updated.")
else:
    print("❌ CHANGELOG.md not found.")

# 3. Stage and commit
os.system("git add PROJECT_STATUS.md CHANGELOG.md")

# Generate commit message
commit_parts = []
if version_tag:
    commit_parts.append(f"📦 {version_tag}")
if changelog_updated:
    commit_parts.append("📝 updated changelog")
if status_updated:
    commit_parts.append("📊 updated project status")
commit_msg = ": ".join([commit_parts[0], ", ".join(commit_parts[1:])]) if len(commit_parts) > 1 else commit_parts[0]

print(f"🧠 Auto-generated commit message: {commit_msg}")
confirm = input("Use this message? [Y/n]: ").strip().lower()
if confirm == "n":
    print("✏️ Enter custom commit message:")
    commit_msg = input("> ")

os.system(f"git commit -m \"{commit_msg}\"")
os.system(f"git push origin {branch}")

# 4. Tag the repo
os.system(f"git tag {version_tag}")
os.system(f"git push origin {version_tag}")
print(f"🏷️ Repo tagged with {version_tag}")

# 5. Log to release.log
with open(log_path, "a") as log_file:
    log_file.write(f"{datetime.now().isoformat()} — {version_tag} — {commit_msg}\n")
print("🗂️ Logged release to release.log")

print("🚀 All done.")

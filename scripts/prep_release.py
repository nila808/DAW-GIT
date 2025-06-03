#!/usr/bin/env python3

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ui_strings import ROLE_KEY_MAIN_MIX

# Paths
root = Path(__file__).resolve().parent.parent
status_path = root / "PROJECT_STATUS.md"
changelog_path = root / "CHANGELOG.md"
log_path = root / "release.log"
marker_path = root / "PROJECT_MARKER.json"

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
    except Exception:
        return "- No recent commits found."

# ✅ Always run tests first
print("🧪 Running tests before release...")
if os.system("pytest") != 0:
    print("❌ Tests failed — release aborted.")
    exit(1)
print("✅ All tests passed.\n")

# 🔖 Require version tag input
version_tag = ""
while not version_tag:
    version_tag = input("🔖 Enter version tag (e.g. v1.0.4-ui-polish): ").strip()
    if not version_tag:
        print("❌ Version tag is required to continue.")
    elif version_tag.lower() in ["push-it", "push"]:  # prevent accidental reuse
        print("⚠️ Invalid tag name. Please use a semantic version like v1.0.4.")
        version_tag = ""

# 1. Update PROJECT_STATUS.md date
status_updated = False
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

# 2. Update CHANGELOG.md
author = os.getenv("USER") or os.getenv("USERNAME") or "unknown"
recent_commits = get_recent_commits()
entry = f"\n\n## [{version_tag}] – {datetime.today().strftime('%Y-%m-%d')}\n**Author:** @{author}\n{recent_commits}\n"

changelog_updated = False
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

# 3. Update PROJECT_MARKER.json
if marker_path.exists():
    with open(marker_path, "r") as f:
        marker = json.load(f)
    marker["project_version"] = version_tag
    if "metadata" not in marker:
        marker["metadata"] = {}
    if "tags" not in marker["metadata"]:
        marker["metadata"]["tags"] = {}
    marker["metadata"]["tags"]["version_marker"] = version_tag
    with open(marker_path, "w") as f:
        json.dump(marker, f, indent=2)
    print(f"📁 PROJECT_MARKER.json updated with version {version_tag}")
else:
    print("⚠️ PROJECT_MARKER.json not found — skipping.")


# 4. Ensure ROADMAP.md exists and stage it
roadmap_path = root / "ROADMAP.md"
if not roadmap_path.exists():
    print("📘 Creating ROADMAP.md...")
    roadmap_path.write_text("""# 🛣️ DAW Git – Roadmap
_Tracking future features, optimizations, and polish milestones_

---

## 🚀 Core UX & Stability
- [ ] **Snapshot metering** (e.g. `📦 24 Snapshots — 431 MB`)
- [ ] **Modal/message cleanup** (remove dev jargon like “commit ID”)
- [ ] **Loading spinner or progress feedback** (visual indicator during Git operations)
- [ ] **Tag button debounce** (prevent double click tagging)
- [ ] **Snapshot timeline viewer** (visual map of tagged snapshots and branches)

---

## 🧠 Session Logic & Testing
- [ ] **Simulated session test** (mock user saving snapshots, branching, tagging, returning to latest, etc.)
- [ ] **Tag role enforcement** (only 1 Main Mix, many Creative/Alt)
- [ ] **Block SHA edits** (prevent commit ID manipulation from UI)
- [ ] **Tag filter UI** (toggle to show/hide Creative, Alt, Custom tags)
- [ ] **Per-role color coding** in commit history

---

## 🧰 Performance Optimizations
- [x] **Debounced file watchers** (reduce Git noise from frequent `.als` saves)
- [x] **Throttle `update_log()`** (buffer UI redraw during autosave)
- [ ] **Run Git ops in background thread** (non-blocking status/log calls)
- [ ] **Smart file diffing or size delta estimation**
- [ ] **Selective refresh** (only update UI when snapshot set has changed)

---

## 🎛 DAW Features & Workflow
- [ ] **Switch DAW target** (Ableton ↔ Logic toggle)
- [ ] **Auto-open snapshot by role** (e.g. "latest Creative")
- [ ] **Role usage summary** (e.g. "5 Creative, 1 Main Mix")
- [ ] **Export tagged versions** (ZIP download of selected snapshots)
- [ ] **Recent DAW usage tracking**

---

## 🧩 Project-Wide Enhancements
- [ ] **Folder size warnings** (e.g. show alert if >2GB)
- [ ] **Git remote sync** (push snapshots to GitHub/GitLab from app)
- [ ] **Session summary export** (markdown of all tags, branches, notes)
- [ ] **Role-based UI modes** (Artist vs Engineer vs Mixer presets)
- [ ] **Custom project metadata** (BPM, key, collaborators)
""")
    print("✅ ROADMAP.md created.")
else:
    print("📘 ROADMAP.md already exists — not modified.")

# 4. Stage and commit
os.system("git add PROJECT_STATUS.md CHANGELOG.md PROJECT_MARKER.json ROADMAP.md")

# Commit message
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

os.system(f'git commit -m "{commit_msg}"')
os.system(f"git push origin {branch}")

# 5. Tag the repo (if not already tagged)
existing_tags = subprocess.check_output(["git", "tag"], cwd=root).decode().splitlines()
if version_tag in existing_tags:
    print(f"⚠️ Tag {version_tag} already exists. Skipping tag.")
else:
    os.system(f"git tag {version_tag}")
    os.system(f"git push origin {version_tag}")
    print(f"🏷️ Repo tagged with {version_tag}")

# 6. Log to release.log
with open(log_path, "a") as log_file:
    log_file.write(f"{datetime.now().isoformat()} — {version_tag} — {commit_msg}\n")
print("🗂️ Logged release to release.log")

print("🚀 All done.")

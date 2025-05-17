# ✅ DAW Git App — Manual Test Plan

## 📋 Table of Contents

### 🎚️ Project Setup & Git Initialization
1. [Test 1: Setup new project folder](#test-1-setup-new-project-folder)  
2. [Test 2: Setup in existing repo](#test-2-setup-in-existing-repo)  
3. [Test 3: Cancel setup modal](#test-3-cancel-setup-modal)  
4. [Test 4: Setup fails (e.g., no permissions)](#test-4-setup-fails-eg-no-permissions)

### 📁 Project Path & Tracking
5. [Test 5: Change project folder](#test-5-change-project-folder)  
6. [Test 6: Clear project path](#test-6-clear-project-path)  
7. [Test 7: Reopen app with saved path](#test-7-reopen-app-with-saved-path)

### 🧾 Commit Workflow
8. [Test 8: Commit with message + tag](#test-8-commit-with-message--tag)  
9. [Test 9: Auto commit](#test-9-auto-commit)  
10. [Test 10: Commit without .als or .logicx](#test-10-commit-without-als-or-logicx)  
11. [Test 11: Multiple commits visible in table](#test-11-multiple-commits-visible-in-table)

### ⏪ Checkout, Branching, Restore
12. [Test 12: Checkout selected commit](#test-12-checkout-selected-commit)  
13. [Test 13: Return to latest commit](#test-13-return-to-latest-commit)  
14. [Test 14: Start new version line (branch)](#test-14-start-new-version-line-branch)  
15. [Test 15: Restore last backup](#test-15-restore-last-backup)  
16. [Test 16: Switch branches mid-session](#test-16-switch-branches-mid-session)

### 🎼 Launch + File Actions
17. [Test 17: Open latest Ableton file](#test-17-open-latest-ableton-file)  
18. [Test 18: Open latest Logic file](#test-18-open-latest-logic-file)  
19. [Test 19: No DAW project file = skip or error](#test-19-no-daw-project-file--skip-or-error)  
20. [Test 20: Export snapshot](#test-20-export-snapshot)  
21. [Test 21: Import snapshot](#test-21-import-snapshot)

### 🪪 Commit Table Display
22. [Test 22: Branch names shown per commit](#test-22-branch-names-shown-per-commit)  
23. [Test 23: Tag shown per commit](#test-23-tag-shown-per-commit)  
24. [Test 24: Table updates after new commit](#test-24-table-updates-after-new-commit)

### 🛡️ Safety Checks
25. [Test 25: Checkout with uncommitted changes](#test-25-checkout-with-uncommitted-changes)  
26. [Test 26: Detached HEAD warning](#test-26-detached-head-warning)  
27. [Test 27: Untracked files warning on checkout](#test-27-untracked-files-warning-on-checkout)  
28. [Test 28: Commit deletion protected](#test-28-commit-deletion-protected)

### 🧪 System & Stability
29. [Test 29: Launch from app icon (PATH resolves)](#test-29-launch-from-app-icon-path-resolves)  
30. [Test 30: Repo with no commits — table safe](#test-30-repo-with-no-commits--table-safe)  
31. [Test 31: Multi-DAW project detection](#test-31-multi-daw-project-detection)  
32. [Test 32: Corrupt Git repo handling](#test-32-corrupt-git-repo-handling)

---

# 🧪 Test Case Details

## Test 1: Setup new project folder
**Steps:**
1. Launch the app
2. Click “Setup Project”
3. Choose a new folder not under version control

**Expected Result:**  
- Git repo is initialized  
- `.git` folder appears  
- Success modal shown

---

## Test 2: Setup in existing repo
Steps and expected outcome...

---

## Test 3: Cancel setup modal
Steps and expected outcome...

---

## Test 4: Setup fails (e.g., no permissions)
Steps and expected outcome...

---

## Test 5–32
_Stub headings can be expanded during QA rounds or added as needed..._

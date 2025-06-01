# 🎛️ DAW Git App Manual Test Plan (v1.0.2)

This manual test plan mirrors the functionality verified by automated tests, allowing step-by-step testing of every feature confirmed to be "working" in the current version.

---

## ✅ Application Startup

- [ ] App launches without crashing.
- [ ] If last project path is saved, it auto-loads on startup.
- [ ] Status label updates correctly based on:
  - [ ] Git repo presence.
  - [ ] Detached HEAD state.
  - [ ] Current branch + commit.
- [ ] Status label shows “✅ 🎧 On version line — 🎵 Version Line: X — Current take: Y” if on branch with role.
- [ ] Status label shows “⚠️ Git status error: HEAD is a detached symbolic reference...” if detached.
- [ ] Status label detects unsaved changes or recently modified `.als`.

---

## 🧠 Commit Logic

- [ ] Commit fails if no `.als` or `.logicx` present.
- [ ] Commit modal allows user to enter a message.
- [ ] If cancelled, no commit is made.
- [ ] Auto-commit works in test mode.
- [ ] Commit history updates after a commit.
- [ ] Commits show in reverse-chronological order.
- [ ] Tooltip on commit shows full SHA.
- [ ] Branches are listed for each commit row.
- [ ] Current checked out commit is highlighted.

---

## 🌿 Branch & Version Line Management

- [ ] “🎼 Start New Version Line” prompts for branch name.
- [ ] If branch exists, warning shown and no action.
- [ ] If detached HEAD, new branch is created safely from current commit.
- [ ] `.version_marker` file is created and committed.
- [ ] `auto_placeholder.als` is created if no `.als` present.
- [ ] Branch switch works safely with:
  - [ ] Confirmation if unsaved changes.
  - [ ] Error shown if branch doesn’t exist and user cancels.
- [ ] UI updates after switching.

---

## 🎛️ Commit Roles (Main Mix / Creative Take / Alt Mixdown)

- [ ] Clicking a mix role button sets role for current commit.
- [ ] Role persists in metadata and is restored on reload.
- [ ] Role appears in third column of commit history table.
- [ ] Only one role per commit; latest selected one wins.
- [ ] Role button is highlighted after selection.

---

## 🧪 Checkout and Restore

- [ ] Clicking on a commit row checks it out.
- [ ] If uncommitted changes, prompt shown and cancel prevents checkout.
- [ ] Status label updates after checkout.
- [ ] “🎧 Open This Version in Ableton” button launches correct `.als`.

---

## 🗑️ Deleting Commits

- [ ] Commit is deleted from history on confirm.
- [ ] Deleted commit disappears from table.
- [ ] Deletion is blocked if HEAD is at commit.
- [ ] Safe backup is created if unsaved changes.

---

## 🛟 Safety Features

- [ ] App detects detached HEAD and warns user.
- [ ] “Return to Latest” resets HEAD to main tip.
- [ ] If no `.als` in commit, warning shown and no commit allowed.
- [ ] Status label shows dirty state if `.als` file modified recently.

---

## 🧹 Untracked Files

- [ ] Untracked folders or files (e.g. `Backup/`) are ignored but noted.
- [ ] Do not trigger dirty state unless `.als` or `.logicx` is modified.
- [ ] Status label remains clean if only untracked junk is present.

---

## 📜 Misc UI and UX

- [ ] Commit message format is `[#N - abcd123] - Short msg (X commits ago)`.
- [ ] Branch dropdown shows all available branches.
- [ ] Active branch is highlighted in dropdown.
- [ ] Commit log auto-scrolls to selected row.
- [ ] UI doesn't freeze when checking out or committing.

---

## 📦 Project File Detection

- [ ] App prefers `.als` over `.logicx` if both present.
- [ ] Placeholder files are skipped when loading most recent.

---

## 🚧 Not Yet Covered

- [ ] Drag-and-drop file addition.
- [ ] Remote pushing / pulling.
- [ ] Git LFS usage.
- [ ] App bundle deployment.

---

_Last updated: 2025-05-17_
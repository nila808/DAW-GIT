
# 🌲 StudioGit Application Workflow (UX + Messaging Tree)

This document outlines the **StudioGit application workflow**, covering key version control features (committing, branching, switching) and how **user-facing messaging** maps to each.

---

## 📁 1. Load a Project Folder

```
User Action: Open project folder
System: Check for Git repo
```

- **If no project folder set:**
  > 🎉 Welcome to DAW Git — no project folder selected.

- **If Git repo found:**
  > 🎵 Session branch: main — 🎧 Take: version 4  
  > ✅ Project loaded successfully

---

## 💾 2. Save a Snapshot (Commit)

```
User Action: Click "Save Snapshot"
Preconditions: DAW file exists, changes present
```

- **Success:**
  > ✅ Snapshot Saved  
  > Branch: main  
  > Commit: abc1234

- **Error:**
  > ❌ No changes to save  
  > 🎛️ Please initialize version control before saving your project.

---

## 🕊️ 3. Checkout Previous Snapshot

```
User Action: Select and load old snapshot from history table
System: Git checkout (detached HEAD)
```

- **Status update:**
  > ℹ️ Detached snapshot — not on an active version line  
  > 🎧 Snapshot {abc1234} loaded — read-only mode...

- **Modal:**
  > 🧭 You’re previewing a saved snapshot.  
  > This version is read-only — perfect for exploring or reference.  
  > To create a new take, click 📝 Start New Version Line.

---

## 📝 4. Start New Version Line

```
User Action: Click “Start New Version Line”
System: Create new branch at current snapshot, auto-commit marker
```

- **Message:**
  > 🎼 Start new version line: {branch}  
  > 🎵 Session branch: {branch} — 🎧 Take: version 1

---

## 🔀 5. Switch Between Version Lines

```
User Action: Choose a different version line from dropdown
```

- **Warning if changes present:**
  > 🎧 You’ve made changes that aren’t saved inside your editable version.  
  > Please save your session (e.g., use 📝 Start New Version Line) before switching.

- **Success:**
  > 🎚️ You’re now working on version line: {branch}

- **If already there:**
  > 🎚️ You're already on this version line: {branch}

---

## 🎯 6. Return to Latest

```
User Action: Click “Return to Latest”
System: Rejoin HEAD of last known branch
```

- **Message:**
  > ✅ Latest take loaded — you're back on session line: ‘main’

---

## 🎧 7. Open Project in DAW

```
User Action: Click “Open This Version in DAW”
System: Load editable snapshot from working copy
```

- **In snapshot:**
  > Read-only preview — edits not saved unless version line is created

- **On version line:**
  > Launches editable DAW session

---

## 💬 UX Message Summary

| Trigger                     | Message Theme                               |
|----------------------------|---------------------------------------------|
| No project folder          | Onboarding / Project Setup                  |
| New commit (snapshot)      | Confirmation + SHA                          |
| Checkout old snapshot      | Read-only + offer to start new version      |
| Detached warning           | Status bar + modal when editing is blocked  |
| New version line           | Branch switch + confirmation                |
| Return to latest           | You're now editable again                   |
| Unsaved changes            | Friendly safety warning                     |

---

_Last updated: v1.1.7 StudioGit UX Framework_

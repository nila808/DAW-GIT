# 🛣️ DAW Git – Roadmap
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

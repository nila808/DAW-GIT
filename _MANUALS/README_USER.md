# DAWGitApp User Manual

Welcome to DAWGitApp — a version control assistant tailored for music producers using Ableton, Logic Pro, and other DAWs.

---

## 🎛 What It Does

DAWGitApp lets you:
- Track your DAW project folder with Git
- Commit changes with messages and optional tags
- Quickly snapshot your progress
- See a history of your commits
- Restore or tag previous versions
- Export/import project snapshots

---

## 🧭 Basic Usage

1. **Launch the App**
   ```
   ./launch_daw_git.sh
   ```

2. **Select a Project Folder**
   - The app remembers your last used folder.
   - You can change this using “Change Project Folder”.

3. **Commit Your Work**
   - Enter a commit message
   - Add a tag (optional)
   - Click “COMMIT CHANGES”

4. **Auto-Commit Option**
   - Use the “AUTO COMMIT” button for fast snapshots
   - This uses a default message and tag

5. **Restore or Export Snapshots**
   - Use “Export Snapshot” to save a project version
   - Use “Import Snapshot” to load it back

6. **View Commit History**
   - See all recent commits
   - Tags, IDs, authors, and messages included
   - “Show Current Commit” highlights the active one

7. **Flashing Indicator**
   - An orange dot appears when you have unsaved changes

---

## 🗂 Recommended Project Structure

```
Music Production/
├── Originals/
│   └── ProjectA/
├── Remixes/
│   └── ArtistX_Remix/
```

Each project folder can be tracked independently by DAWGitApp.

---

## 🛠 Requirements

- Python 3.12
- PyQt6
- Git + Git LFS (optional)

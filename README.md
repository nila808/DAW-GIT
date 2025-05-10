# DAWGitApp

**DAWGitApp** is a PyQt6-based Git versioning tool designed specifically for music producers using DAWs like Ableton, Logic Pro, and Pro Tools. It provides an intuitive GUI for managing project snapshots, commits, and backups — without touching the command line.

---

## 🎛 Features

- 📁 Project folder tracking with persistent path saving
- 💾 One-click Git setup and initial commit
- 📝 Commit messages and optional tag input
- 📜 Git history viewer with checkout controls
- 🧠 Backup system for unsaved changes
- 🔁 Snapshot export/import system
- ☁️ Optional remote push integration
- 🎨 Themed UI with clean PyQt6 design

---

## 🧰 Tech Stack

| Component      | Stack                |
|----------------|----------------------|
| GUI            | PyQt6                |
| Git integration| GitPython + subprocess |
| Platform       | macOS (primary), Linux tested |
| Build system   | PyInstaller (DMG-ready) |
| Test suite     | Pytest + pytest-qt    |

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone git@github.com:yourusername/DAWGitApp.git
cd DAWGitApp
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv daw-git-env
source daw-git-env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the app

```bash
./launch_daw_git.sh
```

---

## 🧪 Run Tests

```bash
./run_tests.sh
```

---

## 📦 Build macOS .app Bundle

```bash
./setup_and_build.sh
```

This uses PyInstaller to generate a standalone `.app` and places it in `dist/`.

---

## 🛡️ .gitignore Included

The `.gitignore` is optimized to ignore:
- Python cache and virtualenvs
- macOS trash files
- PyInstaller build folders
- Snapshot/Backup folders
- Personal DAW project config

---

## 👨‍🎤 Author

Built by [@yourusername](https://github.com/yourusername) — for producers who want version control that speaks DAW.

---

## 🌀 License

MIT (or add your preferred license here)

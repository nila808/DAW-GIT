# DAWGitApp Developer Guide

This document helps developers and contributors set up and maintain the DAWGitApp codebase.

---

## 🧱 Architecture

- GUI Framework: PyQt6
- Git Integration: GitPython + subprocess
- Cross-platform: Developed/tested on macOS
- Target Use: DAW projects (Ableton .als, Logic .logicx, etc.)

---

## 🧰 Setup

1. **Clone and Navigate**
   ```bash
   git clone git@github.com:yourname/DAWGitApp.git
   cd DAWGitApp
   ```

2. **Activate Virtualenv**
   ```bash
   python3 -m venv daw-git-env
   source daw-git-env/bin/activate
   ```

3. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the App**
   ```bash
   ./launch_daw_git.sh
   ```

---

## 🧾 Project Structure

```
DAWGitApp/
├── daw_git_gui.py
├── launch_daw_git.sh
├── setup_and_build.sh
├── tests_dawgit/
│   └── README_TESTS.md
├── styles/
├── icon.png
```

---

## 🔐 Security Considerations

- Subprocess input is list-based to avoid shell injection
- Project paths are resolved using pathlib for safety
- Remote push is opt-in (via checkbox)
- Future builds should include macOS sandbox permissions in Info.plist

---

## 📦 DMG / App Build

```bash
./setup_and_build.sh
```

- Uses PyInstaller with icon support
- Output is placed in `/dist/DAW Git.app`

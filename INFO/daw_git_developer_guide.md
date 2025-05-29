
# 🎛️ DAW Git App – Developer Method Guide

The **DAW Git App** is a Python-based desktop GUI application built with **PyQt6** and integrated with **Git** and **Git LFS**. It helps music producers version-control DAW projects (Ableton and Logic Pro), manage snapshots, branches, and safety backups through an intuitive UI.

## 📁 Project File Overview
- `daw_git_gui.py`: Main and primary code file with GUI logic, Git integration, and snapshot management.

## 🛠️ Core Class
- **`DAWGitApp(QMainWindow)`**: Central application window and logic container.

## 📌 Initialization Methods
- `__init__()`: Initializes app, loads project paths, Git, and UI.
- `setup_ui()`: Sets up GUI components.

## 🎚️ UI and Workflow Methods
- `maybe_show_welcome_modal()`: Shows welcome modal on startup.
- `run_setup()`: Initializes Git setup for project folders.
- `change_project_folder()`: Change tracked DAW folder.
- `load_saved_project_path()`: Loads last project path.

## 📥 Git Repository Management Methods
- `init_git()`: Initializes or loads Git repository.
- `bind_repo()`: Updates repo after Git operations.
- `commit_changes()`: Commits user changes.
- `auto_commit()`: Auto-commits without manual intervention.

## 🌳 Branching and Snapshot Management
- `start_new_version_line()`: Starts a new Git branch.
- `switch_branch()`: Safely switches branches.
- `checkout_selected_commit()`: Checks out specific commits.
- `return_to_latest_clicked()`: Returns to main branch from snapshot state.

## 🔄 Backup and Safety Features
- `backup_unsaved_changes()`: Backs up unsaved changes.
- `stash_uncommitted_changes()`: Stashes unsaved changes.
- `clean_blocking_files()`: Removes problematic files.

## 🗃️ Snapshot Export/Import
- `export_snapshot()`: Exports current snapshot.
- `import_snapshot()`: Imports external snapshot.

## 🏷️ Role and Tag Management
- `assign_commit_role()`: Assigns roles to commits.
- `tag_main_mix()`, `tag_creative_take()`, `tag_alt_mix()`: Tagging convenience methods.
- `tag_custom_label()`: Custom tagging.

## 📜 Version History and UI Updates
- `load_commit_history()`: Loads commit history into UI.
- `update_status_label()`: Updates status labels.
- `update_role_buttons()`: Manages role buttons state.

## 🔔 User Messaging
- `show_status_message()`: Status bar messages.
- `_show_info()`, `_show_warning()`, `_show_error()`: Message boxes.

## ⚙️ Utility and Helper Methods
- `get_latest_daw_project_file()`: Retrieves recent DAW files.
- `open_latest_daw_project()`: Opens latest DAW project.
- `resource_path()`: Resource path handling.

## 📋 Settings and Persistence
- `save_last_project_path()`: Saves project path.
- `load_commit_roles()`, `save_commit_roles()`: Commit roles persistence.
- `save_project_marker()`, `load_project_marker()`: Metadata persistence.

## 🐞 Debugging and Development Helpers
- `custom_env()`: Environment settings for subprocess.
- `safe_single_shot()`: Safe QTimer setup.

## 📍 Workflow Connections (Simplified)
1. **Startup** → `__init__()` → `load_saved_project_path()` → `init_git()`.
2. **Snapshot Save** → "💾 Save Snapshot" → `commit_changes()` → UI refresh.
3. **Branching** → "🎼 Start New Version Line" → `start_new_version_line()` → UI update.
4. **Snapshot Restore** → "🎧 Load This Snapshot" → `checkout_selected_commit()` → open DAW.
5. **Tagging** → UI tagging → methods (`tag_main_mix()`, etc.) → persist and update roles.
6. **Safety** → Risky operations → backup/stash via safety methods.

## 🚩 Key UI Buttons → Methods
| Button | Method |
|--------|--------|
| 💾 Save Snapshot | `commit_changes()` |
| 🎼 Start New Version Line | `start_new_version_line()` |
| 🔀 Switch Version Line | `switch_branch()` |
| 🎧 Load This Snapshot | `checkout_selected_commit()` |
| 🎯 Return to Latest | `return_to_latest_clicked()` |
| 📂 Change Project Folder | `change_project_folder()` |
| 📥 Import Snapshot | `import_snapshot()` |
| 📤 Export Snapshot | `export_snapshot()` |
| 🗑️ Delete This Snapshot | `delete_selected_commit()` |
| 🌟/🎨/🎚️ Tag Buttons | Tagging methods (`tag_main_mix()`, etc.) |

---

**🎓 Junior Developer Tip**:  
Start by interacting with the UI to learn method triggers. Use `[DEBUG]` log statements for troubleshooting.

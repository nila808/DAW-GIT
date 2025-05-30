# ui_strings.py

# Commit & Snapshot
COMMIT_SUCCESS_TITLE = "✅ Snapshot Saved"
COMMIT_SUCCESS_MSG = "Branch: {branch}\nCommit: {sha}"
COMMIT_INFO_EMPTY = "No commits yet."
CURRENT_COMMIT_TITLE = "Current Snapshot"

# Auto-save
AUTO_SAVE_TITLE = "Auto Save Complete"

# Return to Latest
RETURN_TO_LATEST_TITLE = "🎯 Return to Latest"
RETURN_TO_LATEST_MSG = "You're now back on the latest version line: '{branch}'"

# Snapshot Viewing
SNAPSHOT_INFO_TITLE = "🎧 Snapshot loaded"
SNAPSHOT_INFO_MSG = (
    "🎧 Snapshot loaded — {label}\n\n"
    "🕒 Committed: {date} ({diff})\n"
    "📦 This version is read-only — explore freely.\n\n"
    "🎼 Want to make edits? Click “🎼 Start New Version Line” to begin a new take."
)

SNAPSHOT_EDIT_BLOCK_TOOLTIP = "🎧 Snapshot mode: You’re previewing an old take. Start a new Snapshot to edit and save in your DAW."
SNAPSHOT_ALREADY_VIEWING_TITLE = "Already Viewing Snapshot"
SNAPSHOT_ALREADY_VIEWING_MSG = "🎧 You're already previewing this Snapshot.\n\nCommit ID: {sha}"
SNAPSHOT_EDIT_BLOCK_TOOLTIP = "🎧 Snapshot mode: You’re previewing an old take. Start a new Snapshot to edit and save in your DAW."
DIRTY_EDIT_WARNING = (
    "🎧 Your current editing session hasn’t been saved.\n\n"
    "Please save a Snapshot to keep this take before switching."
)

UNSAVED_CHANGES_TITLE = "Unsaved Changes Detected"
UNSAVED_CHANGES_WARNING = (
    "🎧 Your latest take has unsaved edits.\n\n"
    "To keep your progress safe, please **Save a Snapshot** "
    "or **Start a New Version Line** before switching versions."
)

# Restore
PROJECT_RESTORED_TITLE = "Project Restored"
PROJECT_RESTORED_MSG = "✅ Version restored.\n\n🎛️ Commit ID: {sha}"

# Branch switching
ALREADY_ON_BRANCH_TITLE = "Already on Branch"
ALREADY_ON_BRANCH_MSG = "🎚️ You're already on this version line:\n\n{branch}"

# Backup
BACKUP_RESTORED_TITLE = "Backup Restored"
BACKUP_RESTORED_MSG = "✅ Restored files from: {path}"
NO_BACKUP_FOUND_MSG = "There are no backup folders for this project."

# Errors
NO_REPO_TITLE = "No Repo"
NO_REPO_MSG = "🎛️ Please initialize version control first."

ALREADY_ON_COMMIT_TITLE = "Already Viewing Snapshot"
ALREADY_ON_COMMIT_MESSAGE = (
    "🎧 Already viewing this snapshot.\n\n"
    "Commit ID: {sha}"
)

NO_SNAPSHOT_SELECTED_MSG = "Please select a version row to load."
NO_SELECTION_TITLE = "No Selection"
NO_SELECTION_MSG = "Please select a snapshot to delete."
DELETE_ROOT_ERROR_TITLE = "Can't Delete Root Commit"
DELETE_ROOT_ERROR_MSG = "The first commit in this version history can’t be removed."

INVALID_LABEL_TITLE = "Invalid Label"
INVALID_LABEL_MSG = "❌ Please enter a valid label."

COMMIT_NOT_FOUND_TITLE = "Commit Not Found"
COMMIT_NOT_FOUND_MSG = "❌ Could not find a valid commit at this row."

DETACHED_HEAD_TITLE = "Detached HEAD"
DETACHED_HEAD_MSG = "⚠️ You’re previewing a snapshot. Return to a version line to switch."

# Generic
HEADS_UP_TITLE = "Heads Up"

NO_REPO_TITLE = "🎛️ Project Not Set Up"
NO_REPO_MSG = "Please load or set up a DAW project folder before continuing."

NO_REPO_COMMIT_TITLE = "No Repo"
NO_REPO_COMMIT_MSG = "🎛️ Please initialize version control before saving your project."

NO_REPO_STATUS_LABEL = "❌ No Git repo loaded."

NO_REPO_SAVE_MSG = "🎛️ Please initialize version control before saving your project."


UNSAFE_DIRTY_EDITS_TITLE = "🎛️ Unsaved Session Changes Detected"
UNSAFE_DIRTY_EDITS_MSG = (
    "🎹 You’ve made changes in your DAW.\n"
    "SAVE your project in Ableton or Logic before continuing.\n\n"
    "Then click 📝 Start New Version Line to capture this version in DAW Git.\n\n"
    "{file_list}"
)
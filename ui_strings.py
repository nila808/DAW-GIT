# ui_strings.py

# Snapshot Role Labels
TAG_LABELS = {
    "main": "🎼 Save Snapshot as New Version",
    "alt": "🎭 Alt Mixdown",
    "creative": "🧪 Creative Take"
}

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

# Toast Feedback – Return to Latest
RETURN_TO_LATEST_SUCCESS = "🎼 Back on the MAIN version line."
RETURN_TO_LATEST_FAIL = (
    "🎧 Couldn't return to your MAIN version. "
    "Try a different version line or select a saved session from the snapshot list."
)
ALREADY_ON_MAIN = "Already on version line 'MAIN'. No action needed."

# Snapshot Viewing
SNAPSHOT_ALREADY_VIEWING_TITLE = "Already Viewing Snapshot"
SNAPSHOT_ALREADY_VIEWING_MSG = "🎧 You're already previewing this version.\n\nCommit ID: {sha}"

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

NO_SNAPSHOT_SELECTED_MSG = "Please select a version row to load."
NO_SELECTION_TITLE = "No Selection"
NO_SELECTION_MSG = "Please select a snapshot to delete."
DELETE_ROOT_ERROR_TITLE = "Can't Delete Root Commit"
DELETE_ROOT_ERROR_MSG = "The first commit in this version history can’t be removed."

INVALID_LABEL_TITLE = "Invalid Label"
INVALID_LABEL_MSG = "❌ Please enter a valid label."

COMMIT_NOT_FOUND_TITLE = "Commit Not Found"
COMMIT_NOT_FOUND_MSG = "❌ Could not find a valid commit at this row."

# Detached Head/Snapshot
DETACHED_HEAD_TITLE = "📸 Exploring Snapshot"
DETACHED_HEAD_MSG = (
    "📦 You’re browsing a snapshot — this version is read-only.\n\n"
    "To continue working from here, click:\n"
    "🎼 Save Snapshot as New Version"
)
DETACHED_HEAD_OPTIONS = [
    "🎼 Save Snapshot as New Version",
    "🔁 Return to Latest",
    "Cancel"
]

SNAPSHOT_CONFIRMATION_TITLE = "📸 You're Exploring a Snapshot"
SNAPSHOT_CONFIRMATION_MSG = (
    "📸 You're exploring an earlier version.\n"
    "This will open in an editable copy so you can try ideas safely.\n\n"
    "💡 To save changes, use ‘🎼 Save Snapshot as New Version’.\n\n"
    "Continue?"
)

# Generic
HEADS_UP_TITLE = "Heads Up"

NO_REPO_TITLE = "🎛️ Project Not Set Up"
NO_REPO_MSG = "Please load or set up a DAW project folder before continuing."

NO_REPO_COMMIT_TITLE = "No Repo"
NO_REPO_COMMIT_MSG = "🎛️ Please initialize version control before saving your project."

NO_REPO_STATUS_LABEL = "❌ No Git repo loaded."

NO_REPO_SAVE_MSG = "🎛️ Please initialize version control before saving your project."


# 📥 Commit & Snapshot
COMMIT_SUCCESS_LABEL = "✅ Committed: {sha}"
COMMIT_SUCCESS_TITLE = "✅ Snapshot Saved"
COMMIT_SUCCESS_MSG = "Branch: {branch}\nCommit: {sha}"
COMMIT_FAILED_LABEL = "❌ Couldn’t save snapshot:\n{error_msg}"
COMMIT_INFO_EMPTY = "No commits yet."
CURRENT_COMMIT_TITLE = "Current Snapshot"
COMMIT_NOW_BUTTON = "💾 Commit Now"
COMMIT_READY_LABEL = "📦 Ready to commit"
COMMIT_PAGE_TITLE = "📥 Commit Snapshot"
COMMIT_MESSAGE_PLACEHOLDER = "Describe what changed in this snapshot"
COMMIT_MESSAGE_REQUIRED_ERROR = "❌ Commit message is required."

# 🔁 Auto-Save
ENABLE_AUTO_SNAPSHOT_LABEL = "Enable Auto-Snapshot"
AUTO_SAVE_SNAPSHOTS_LABEL = "🎹 Auto-Save Snapshots"
AUTO_SAVE_TITLE = "Auto Save Complete"

# 🔙 Return to Latest
RETURN_TO_LATEST_TITLE = "🎯 Return to Latest"
RETURN_TO_LATEST_MSG = "You're now back on the latest version line: '{branch}'"
RETURN_TO_LATEST_BTN = "🎯 Return to Latest"
RETURN_TO_LATEST_TOOLTIP = "Return to the most recent snapshot on your version line"

# 🎧 Snapshot Viewing
SNAPSHOT_INFO_TITLE = "🎧 Snapshot loaded"
SNAPSHOT_INFO_MSG = (
    "🎧 Snapshot loaded — {label}\n\n"
    "🕒 Committed: {date} ({diff})\n"
    "📦 This version is read-only — explore freely.\n\n"
    "🎼 Want to make edits? Click “🎼 Start New Version Line” to begin a new take."
)
SNAPSHOT_ALREADY_VIEWING_TITLE = "Already Viewing Snapshot"
SNAPSHOT_ALREADY_VIEWING_MSG = "🎧 You're already previewing this Snapshot.\n\nCommit ID: {sha}"
SNAPSHOT_EDIT_BLOCK_TOOLTIP = "🎧 Snapshot mode: You’re previewing an old take. Start a new Snapshot to edit and save in your DAW."
DIRTY_EDIT_WARNING = (
    "🎧 Your current editing session hasn’t been saved.\n\n"
    "Please save a Snapshot to keep this take before switching."
)
SNAPSHOT_VIEWING_WARNING_TITLE = "Currently Viewing Snapshot"
SNAPSHOT_VIEWING_WARNING_MSG = (
    "🎧 You’re currently exploring a snapshot.\n\n"
    "Switching now will move you to a saved version line.\n\nContinue?"
)
SNAPSHOT_LOADED_STATUS_LABEL = "✅ Snapshot {sha} loaded — read-only mode. Explore or start a new version line."
SNAPSHOT_READY_STATUS_LABEL = "📦 Ready"
SNAPSHOT_BROWSER_TITLE = "🎧 Snapshot Browser"
LOAD_SNAPSHOT_BUTTON = "🎧 Load This Snapshot"

# 🌱 Version Line
START_VERSION_LINE_BTN = "🎼 Start New Version Line"
START_VERSION_LINE_BUTTON = "🎼 Start New Version Line"
START_VERSION_LINE_TITLE = "🎼 Start New Version Line"
START_VERSION_LINE_PROMPT = (
    "Name your new version line (e.g. 'alt_take2', 'live_mix', or 'idea_bounce'):\n\n"
    "✅ Use letters, numbers, dashes, or underscores.\n"
    "🚫 Avoid spaces, slashes, or special characters."
)
VERSION_LINE_COMMIT_MSG = "🎼 Start new version line: {branch}"
VERSION_LINE_SUCCESS_LABEL = "🌱 You’re now working on version line: {branch}"
VERSION_LINE_CREATED_TITLE = "Version Line Created"
VERSION_LINE_CREATED_CONFIRM_MSG = "🌱 You’re now working on version line:\n\n{branch}"
SESSION_STATUS_LABEL = "🎵 Session branch: {branch} — 🎧 Take: version {count}"

# 🧩 Role Tagging
ROLE_MAIN_MIX_LABEL = "Main Mix"
ROLE_CREATIVE_LABEL = "Creative"
ROLE_ALT_MIX_LABEL = "Alt Mix"
ROLE_MAIN_TOOLTIP = "🌟 Mark as Final Mix"
ROLE_CREATIVE_TOOLTIP = "🎨 Mark as Creative Version"
ROLE_ALT_TOOLTIP = "🎛️ Mark as Alternate Mix"
ROLE_CUSTOM_TOOLTIP = "✏️ Add Custom Tag"
TAG_MAIN_MIX_BUTTON = "🌟 Main Mix"
TAG_MAIN_MIX_TOOLTIP = "Tag the selected snapshot as your Main Mix"
TAG_CREATIVE_BUTTON = "🎨 Creative"
TAG_CREATIVE_TOOLTIP = "Tag the selected snapshot as a creative take"
TAG_ALT_MIX_BUTTON = "🎛️ Alt Mix"
TAG_ALT_MIX_TOOLTIP = "Tag the selected snapshot as an alternate version"
TAG_SNAPSHOT_BUTTON = "🎭 Tag This Take"
ASSIGN_ROLE_BUTTON = "🎵 Assign Mix Role"

# 💾 Quick Commit / Snapshot Tools
QUICK_SAVE_BUTTON = "💾 Quick Save"
QUICK_SAVE_TOOLTIP = "Save a snapshot using the most recent commit message"
OPEN_COMMIT_PANEL_BUTTON = "✏️ Open Commit Panel"
OPEN_COMMIT_PANEL_TOOLTIP = "Open full snapshot editor"
OPEN_IN_DAW_LABEL = "🎧 Open This Version in DAW"
OPEN_IN_DAW_BUTTON = "🎧 Open This Version in Ableton"
OPEN_IN_DAW_TOOLTIP = "Launch Ableton with the checked-out snapshot"
WHERE_AM_I_BUTTON = "📍 Where Am I?"


# 🛠 Project Setup
STEP1_CHOOSE_PROJECT_FOLDER_LABEL = "🎚️ Step 1: Choose your Ableton or Logic project folder"
PROJECT_SETUP_TITLE = "🎵 Project Setup"
START_TRACKING_BUTTON = "Start Tracking"
LOAD_ALTERNATE_SESSION_BUTTON = "Load Alternate Session"
CHANGE_PROJECT_FOLDER_BUTTON = "Change Project Folder"
CLEAR_PROJECT_BUTTON = "Clear Saved Project"
EXPORT_SNAPSHOT_BUTTON = "Export Snapshot"
IMPORT_SNAPSHOT_BUTTON = "Import Snapshot"
RESTORE_BACKUP_BUTTON = "Restore Last Backup"
PUSH_AFTER_SNAPSHOT_LABEL = "Push to remote after snapshot"
CONNECT_REMOTE_BUTTON = "🔗 Connect to Remote Repo"

# 🌳 Branch Manager
BRANCH_MANAGER_TITLE = "🌳 Branch Manager"
SWITCH_BRANCH_BUTTON = "🔀 Switch Branch"
SWITCH_VERSION_LINE_BUTTON = "🔀 Switch Version Line"
SESSION_BRANCH_UNKNOWN_LABEL = "Session branch: unknown • Current take: unknown"
NO_ACTIVE_VERSION_LINE_LABEL = "🎚️ No active version line"
NO_REPO_LOADED_LABEL = "⚠️ No Git repo loaded."
BRANCHES_LOADED_LABEL = "✅ {count} branches loaded."

# ⚠️ Errors & Warnings
UNSAVED_CHANGES_TITLE = "Unsaved Changes Detected"
UNSAVED_CHANGES_WARNING = (
    "🎧 Your latest take has unsaved edits.\n\n"
    "To keep your progress safe, please **Save a Snapshot** "
    "or **Start a New Version Line** before switching versions."
)
ALREADY_ON_BRANCH_TITLE = "Already on Branch"
ALREADY_ON_BRANCH_MSG = "🎚️ You're already on this version line:\n\n{branch}"
ALREADY_ON_COMMIT_TITLE = "Already Viewing Snapshot"
ALREADY_ON_COMMIT_MESSAGE = "🎧 Already viewing this snapshot.\n\nCommit ID: {sha}"
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

# ❌ No Repo / Project
NO_PROJECT_SELECTED_TITLE = "No Project Selected"
NO_PROJECT_SELECTED_MSG = (
    "🎛️ No project folder selected. Click 'Setup Project' to start tracking your music session."
)
NO_REPO_TITLE = "🎛️ Project Not Set Up"
NO_REPO_MSG = "Please load or set up a DAW project folder before continuing."
NO_REPO_COMMIT_TITLE = "No Repo"
NO_REPO_COMMIT_MSG = "🎛️ Please initialize version control before saving your project."
NO_REPO_STATUS_LABEL = "❌ No Git repo loaded."
NO_REPO_SAVE_MSG = "🎛️ Please initialize version control before saving your project."

# ♻️ Backup & Restore
PROJECT_RESTORED_TITLE = "Project Restored"
PROJECT_RESTORED_MSG = "✅ Version restored.\n\n🎛️ Commit ID: {sha}"
BACKUP_RESTORED_TITLE = "Backup Restored"
BACKUP_RESTORED_MSG = "✅ Restored files from: {path}"
NO_BACKUP_FOUND_MSG = "There are no backup folders for this project."

# 🧠 General Info / Utilities
EMPTY_LABEL = ""
SNAPSHOT_NOTES_LABEL = "Snapshot Notes:"
AUTO_SAVE_TOGGLE_LABEL = "🎹 Auto-Save Snapshots"
SWITCH_BRANCH_LABEL = "🔀 Switch Version Line"
SHOW_TOOLTIPS_LABEL = "Show Tooltips"
HEADS_UP_TITLE = "Heads Up"
SNAPSHOT_MODE_UNKNOWN_LABEL = "🎧 Snapshot mode: unknown"
STATUS_UNKNOWN_LABEL = "🎚️ Status: unknown"
ACTIVE_BRANCH_UNKNOWN_LABEL = "🎚️ No active version line"
SESSION_INFO_UNKNOWN_LABEL = "Session branch: unknown • Current take: unknown"
COMMIT_UNKNOWN_LABEL = "🎶 Commit: unknown"
CURRENT_COMMIT_UNKNOWN_LABEL = "🎶 Commit: unknown"
UNCOMMITTED_CHANGES_LABEL = "● Uncommitted Changes"
UNSAFE_DIRTY_EDITS_TITLE = "🎛️ Unsaved Session Changes Detected"
UNSAFE_DIRTY_EDITS_MSG = (
    "🎹 You’ve made changes in your DAW.\n"
    "SAVE your project in Ableton or Logic before continuing.\n\n"
    "Then click 📝 Start New Version Line to capture this version in DAW Git.\n\n"
    "{file_list}"
)




















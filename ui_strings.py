# ui_strings.py

# === General App Status ===
STATUS_READY = "Ready"
STATUS_UNKNOWN = "🎚️ Status: unknown"

# === Tab Labels ===
TAB_BRANCH_MANAGER = "🔀 Branch Manager"
TAB_SNAPSHOT_BROWSER = "🎧 Snapshot Browser"
TAB_COMMIT_PAGE = "📥 Commit Page"
TAB_PROJECT_SETUP = "🛠 Project Setup"

# === Snapshot Editing State ===
SNAPSHOT_MODE_UNKNOWN = "🎧 Snapshot mode: unknown"
SNAPSHOT_NO_VERSION_LINE = "🎧 Snapshot mode: Not on an active version line"
SNAPSHOT_READONLY_TOOLTIP = "🎧 Snapshot mode: read-only preview"
SNAPSHOT_EDIT_BLOCK_TOOLTIP = "🎧 Snapshot mode: You’re previewing an old take. Start a new Snapshot to edit and save in your DAW."
SNAPSHOT_EDIT_UNKNOWN = "🎧 Editing: unknown"
DETACHED_HEAD_LABEL = "🔍 Detached snapshot • Not on a version line"
DETACHED_HEAD_MSG = "⚠️ You’re previewing a snapshot. Return to a version line to switch."
SNAPSHOT_EDITABLE_TOOLTIP = "🎚️ You’re editing this take — changes will be saved"
ALREADY_ON_COMMIT_TITLE = "Already on This Snapshot"
ALREADY_ON_COMMIT_MESSAGE = "🎧 You’re already on snapshot {sha}."


# === Snapshot Controls ===
# === Commit / Snapshot Titles ===
COMMIT_SUCCESS_TITLE = "✅ Snapshot Saved"
COMMIT_SUCCESS_MSG = "Branch: {branch}\nCommit: {sha}"
CURRENT_COMMIT_TITLE = "Current Snapshot"
COMMIT_INFO_EMPTY = "No commits yet."
COMMIT_INFO_TITLE = "Commit Info"
COMMIT_REQUIRED_MSG = "❌ Commit message is required."

# === Auto Save ===
AUTO_SAVE_TITLE = "Auto Save Complete"


# === Return to Latest ===
RETURN_TO_LATEST_BTN = "🎯 Return to Latest"
RETURN_TO_LATEST_TITLE = "🎯 Return to Latest"
RETURN_TO_LATEST_MSG = "You're now back on the latest version line: '{branch}'"
TOOLTIP_RETURN_TO_LATEST = "🎯 Return to Latest — get back to your main line"


# === Snapshot Viewing / Feedback ===
SNAPSHOT_INFO_TITLE = "🎧 Snapshot loaded"
SNAPSHOT_INFO_MSG = (
    "🎧 Snapshot loaded — {label}\n\n"
    "🕒 Committed: {date} ({diff})\n"
    "📦 This version is read-only — explore freely.\n\n"
    "🎼 Want to make edits? Click “🎼 Start New Version Line” to begin a new take."
)
SNAPSHOT_LOAD_SUCCESS = "📦 Snapshot loaded — read-only mode"
SNAPSHOT_LOAD_FAILED = "❌ Could not load session."
SNAPSHOT_ALREADY_VIEWING_TITLE = "Already Viewing Snapshot"
SNAPSHOT_ALREADY_VIEWING_MSG = "🎧 You're already previewing this Snapshot.\n\nCommit ID: {sha}"
SNAPSHOT_HISTORY_LOADING = "⏳ Loading snapshot history..."
SNAPSHOT_HISTORY_LOADED = "✅ Snapshot history loaded."
SNAPSHOT_SAVED_AUTODISABLED = "✅ Snapshot saved. Auto-commit disabled until further changes."
SNAPSHOT_SAVED_WAITING = "✅ Snapshot saved. Waiting for new changes."
SNAPSHOT_SAVED_WAITING_TOOLTIP = "✅ Snapshot saved. Waiting for new changes."
DIRTY_EDIT_WARNING = (
    "🎧 Your current editing session hasn’t been saved.\n\n"
    "Please save a Snapshot to keep this take before switching."
)

# === Snapshot Selection / Errors ===
NO_SNAPSHOT_SELECTED_TITLE = "No Snapshot Selected"
NO_SNAPSHOT_SELECTED_MSG = "Please select a version row to load."
NO_VERSION_SELECTED_MSG = "Please select a version to continue."
NO_SELECTION_TITLE = "No Selection"
NO_SELECTION_MSG = "Please select a Take to delete."

# === Commit Errors ===
COMMIT_NOT_FOUND_TITLE = "Take Not Found"
COMMIT_NOT_FOUND_MSG = "❌ Could not find a valid Take at this row."
CANT_DELETE_ROOT_TITLE = "Can't Delete Root"
CANT_DELETE_ROOT_MSG = "The first Take in this Session can’t be removed."
DELETE_FAILED_TITLE = "Delete Failed"
DELETE_FAILED_MSG = "Could not delete this Take."
REBASE_FAILED_TITLE = "Rebase Failed"
REBASE_FAILED_MSG = "Could not rebase changes."
CHECKOUT_FAILED_TITLE = "Checkout Failed"
CHECKOUT_FAILED_MSG = "Could not load this Take."
COULDNT_SWITCH_TITLE = "Couldn’t Switch"
COULDNT_SWITCH_MSG = "An error occurred while switching Sessions."
UNEXPECTED_ERROR_TITLE = "Unexpected Error"
UNEXPECTED_ERROR_MSG = "An unknown error occurred."
UNEXPECTED_ISSUE_TITLE = "Unexpected Issue"
UNEXPECTED_ISSUE_MSG = "⚠️ Something went wrong while preparing your session:\n\n{error}"
SESSION_SETUP_FAILED_MSG = "Something went wrong"
CROSS_BRANCH_COMMIT_MSG = "❌ This commit is from another version line."

# === Backup / Restore ===
NO_BACKUP_FOUND_TITLE = "No Backup Found"
NO_BACKUP_FOUND_MSG = "There are no backup folders for this project."
BACKUP_RESTORED_TITLE = "Backup Restored"
BACKUP_RESTORED_MSG = "✅ Restored files from: {path}"
PROJECT_RESTORED_MSG = "✅ Version restored.\n\n🎛️ Commit ID: {sha}"

# === Repo Setup / Errors ===
NO_REPO_TITLE = "🎛️ Project Not Set Up"
NO_REPO_MSG = "Please load or set up a DAW project folder before continuing."
NO_REPO_COMMIT_TITLE = "No Repo"
NO_REPO_COMMIT_MSG = "🎛️ Please initialize version control before saving your project."
NO_REPO_STATUS_LABEL = "❌ No Git repo loaded."
NO_REPO_SAVE_MSG = "🎛️ Please initialize version control before saving your project."
GIT_NOT_INITIALIZED_MSG = "⚠️ No Git repo initialized."
INVALID_REPO_MSG = "⚠️ Invalid repo setup."
ALREADY_ON_BRANCH_TITLE = "Already on Branch"
ALREADY_ON_BRANCH_MSG = "🎚️ You're already on this version line:\n\n{branch}"

# === Commit Buttons ===
COMMIT_CHANGES_BTN = "🎤 Commit Your Changes"
TAG_SNAPSHOT_BTN = "Tag Snapshot"
START_NEW_VERSION_BTN = "🎼 Start New Version Line"
BTN_COMMIT_NOW = "💾 Commit Now"
BTN_TAG_MAIN_MIX = "🌟 Mark as Final Mix"
BTN_TAG_CREATIVE_TAKE = "🎨 Mark as Creative Version"
BTN_TAG_ALT_MIX = "🎛️ Mark as Alternate Mix"
BTN_TAG_CUSTOM_LABEL = "✏️ Add Custom Tag"
BTN_LAUNCH_DAW_FILE = "🎧 Open This Version in Ableton"
BTN_OPEN_VERSION_IN_DAW = "🎧 Open This Version in DAW"
BTN_OPEN_COMMIT_PANEL = "✏️ Open Commit Panel"
BTN_MAIN_MIX = "🌟 Main Mix"
BTN_CREATIVE_TAKE = "🎨 Creative"
BTN_ALT_MIX = "🎛️ Alt Mix"
BTN_LOAD_SNAPSHOT = "🎧 Load This Snapshot"
BTN_WHERE_AM_I = "📍 Where Am I?"
BTN_QUICK_SAVE = "💾 Quick Save"

# === Project Setup Buttons ===
BTN_CONNECT_REMOTE_REPO = "🔗 Connect to Remote Repo"
CONNECT_REMOTE_BTN = "🔗 Connect to Remote"
BTN_START_TRACKING = "Start Tracking"
BTN_LOAD_ALT_SESSION = "🎹 Load Alternate Session"
BTN_CHANGE_PROJECT_FOLDER = "Change Project Folder"
BTN_CLEAR_SAVED_PROJECT = "Clear Saved Project"
BTN_EXPORT_SNAPSHOT = "Export Snapshot"
BTN_IMPORT_SNAPSHOT = "Import Snapshot"
BTN_RESTORE_BACKUP = "Restore Last Backup"
BTN_SWITCH_VERSION_LINE = "🔀 Switch Version Line"

# === Tooltips ===
TOOLTIP_LAUNCH_DAW_FILE = "Launch Ableton with the checked-out snapshot"
TOOLTIP_LOAD_VERSION_SAFELY = "Load this version of your project safely"
TOOLTIP_SHOW_CURRENT_VERSION = "Show current snapshot version"
TOOLTIP_SAVE_WITH_LAST_MESSAGE = "Save a snapshot using the most recent commit message"
TOOLTIP_TAG_MAIN_MIX = "Tag the selected snapshot as your Main Mix"
TOOLTIP_TAG_CREATIVE = "Tag the selected snapshot as a creative take"
TOOLTIP_TAG_ALT_MIX = "Tag the selected snapshot as an alternate version"
TOOLTIP_OPEN_COMMIT_PANEL = "Open full snapshot editor"
TOOLTIP_OPEN_IN_FINDER = "Click to open in Finder"
TOOLTIP_START_TRACKING_FOLDER = "Start tracking the folder where your current Ableton or Logic project is saved."
TOOLTIP_SWITCH_ALT_VERSION = "Switch to a different creative version of this track"
TOOLTIP_SWITCH_BRANCH = "Switch to another creative path or saved version"
TOOLTIP_ENABLE_AUTOCOMMIT = "Enable to auto-commit when changes are detected"
SETUP_REMOTE_TOOLTIP = "Set up a remote Git URL (e.g. GitHub)"

# === Branch Manager ===
BRANCH_MANAGER_TITLE = "🌳 Branch Manager"
SWITCH_BRANCH_BTN = "🔀 Switch Branch"
NO_REPO_LOADED_MSG = "⚠️ No Git repo loaded."

# === Mix Tags ===
TAG_MAIN_MIX_LABEL = "Main Mix"
TAG_CREATIVE_LABEL = "Creative"
TAG_ALT_LABEL = "Alt Mix"

# === Warnings ===
UNSAVED_CHANGES_TITLE = "Unsaved Changes Detected"
UNSAVED_CHANGES_WARNING = (
    "🎧 Your latest take has unsaved edits.\n\n"
    "To keep your progress safe, please **Save a Snapshot** "
    "or **Start a New Version Line** before switching versions."
)
UNSAFE_DIRTY_EDITS_TITLE = "🎛️ Unsaved Session Changes Detected"
UNSAFE_DIRTY_EDITS_MSG = (
    "🎹 You’ve made changes in your DAW.\n"
    "SAVE your project in Ableton or Logic before continuing.\n\n"
    "Then click 📝 Start New Version Line to capture this version in DAW Git.\n\n"
    "{file_list}"
)

# === Misc ===
HEADS_UP_TITLE = "Heads Up"
HEADS_UP_MSG = "Just a heads up."
NEW_PROJECT_SELECTED_MSG = "🎚️ New project selected."
TRACKING_NONE = "🎵 Tracking: None"
CURRENT_BRANCH_UNKNOWN = "Branch: unknown"
CURRENT_COMMIT_UNKNOWN = "Commit: unknown"
REMOTE_ADDED_TITLE = "Remote Added"
REMOTE_ADDED_MSG = "✅ Remote 'origin' set to:\n{url}"
REMOTE_SETUP_FAILED_TITLE = "Remote Setup Failed"
REMOTE_SETUP_FAILED_MSG = "❌ Could not set up remote:\n\n{error}"
CLICK_TO_OPEN_IN_FINDER_TOOLTIP = "Click to open in Finder"


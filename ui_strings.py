# ui_strings.py

# === General App Status ===
STATUS_READY = "Ready"
STATUS_UNKNOWN = "🎼 No active session line"

# === Tab Labels ===
TAB_BRANCH_MANAGER = "🔀 Session Lines"
TAB_SNAPSHOT_BROWSER = "🎿 Takes Browser"
TAB_COMMIT_PAGE = "📥 Save Take"
TAB_PROJECT_SETUP = "🚰 Project Setup"

# === Snapshot Editing State ===
SNAPSHOT_MODE_UNKNOWN = "🎧 Snapshot mode: (not active)"
SNAPSHOT_NO_VERSION_LINE = "🎿 Take Preview Mode: Not on an active Session Line"
SNAPSHOT_READONLY_TOOLTIP = "🎿 Take Preview Mode — this take is read-only"
SNAPSHOT_EDIT_BLOCK_TOOLTIP = "🎿 Take Preview Mode: You’re previewing an old take. Use + Alt Session to make edits."
SNAPSHOT_EDIT_UNKNOWN = "🎧 Editing: (no take selected)"
DETACHED_HEAD_LABEL = "🔍 Detached Take • Not on a Session Line"
DETACHED_HEAD_MSG = "⚠️ You’re previewing a take. Return to a Session Line to resume editing."
SNAPSHOT_EDITABLE_TOOLTIP = "🎚️ You’re editing this take — changes will be saved"
ALREADY_ON_COMMIT_TITLE = "Already on This Take"
ALREADY_ON_COMMIT_MESSAGE = "🎿 You’re already on take {sha}."
COMMIT_MESSAGE_REQUIRED_STATUS = "❗ Please enter a message before saving this take"


# === Snapshot Controls ===
# === Commit / Snapshot Titles ===
COMMIT_SUCCESS_TITLE = "✅ Take Saved"
COMMIT_SUCCESS_MSG = "Session Line: {branch}\nTake ID: {sha}"
CURRENT_COMMIT_TITLE = "Current Take"
COMMIT_INFO_EMPTY = "No takes saved yet."
COMMIT_INFO_TITLE = "Take Info"
COMMIT_REQUIRED_MSG = "❌ A note is required to save this take."

# === Auto Save ===
AUTO_SAVE_TITLE = "Auto Save Complete"

# === Return to Latest ===
RETURN_TO_LATEST_BTN = "🚀 Resume {branch} Session"
RETURN_TO_LATEST_TITLE = "🚀 Resume Session"
RETURN_TO_LATEST_MSG = "You're now back on the latest session line: '{branch}'"
TOOLTIP_RETURN_TO_LATEST = "🚀 Resume your last editing session"

# === Snapshot Preview Summary ===
SNAPSHOT_PREVIEW_SUMMARY = (
    "🎧 Take Preview Mode: You’re exploring an older take.\n\n"
    "To make edits, click + Alt Session or resume your last session line.\n\n"
    "🎼 Session Line: (read-only preview)   🎙️ Current Take: not yet saved"
)
# === Snapshot Launch Modal ===
SNAPSHOT_CONFIRMATION_TITLE = "🎧 Launching Snapshot"
SNAPSHOT_CONFIRMATION_MSG = (
    "🎧 You’re previewing an older take from your project history.\n\n"
    "Ableton may prompt you to 'Save As' when this version opens.\n\n"
    "🎼 To keep working safely, consider clicking '+ Alt Session' first.\n\n"
    "Would you like to launch this version anyway?"
)

# === Snapshot Viewing / Feedback ===
SNAPSHOT_INFO_TITLE = "🎿 Take loaded"
SNAPSHOT_INFO_MSG = (
    "🎿 Take loaded — {label}\n\n"
    "🕒 Saved: {date} ({diff})\n"
    "📦 This take is read-only — explore freely.\n\n"
    "🎼 Want to make edits? Click “+ Alt Session” to begin a new path."
)
SNAPSHOT_LOAD_SUCCESS = "📦 Take loaded — read-only mode"
SNAPSHOT_LOAD_FAILED = "❌ Could not load take."
SNAPSHOT_ALREADY_VIEWING_TITLE = "Already Viewing Take"
SNAPSHOT_ALREADY_VIEWING_MSG = "🎿 You're already previewing this take.\n\nTake ID: {sha}"
SNAPSHOT_HISTORY_LOADING = "⏳ Loading take history..."
SNAPSHOT_HISTORY_LOADED = "✅ Take history loaded."
SNAPSHOT_SAVED_AUTODISABLED = "✅ Take saved. Auto-commit disabled until further changes."
SNAPSHOT_SAVED_WAITING = "✅ Take saved. Waiting for new changes."
SNAPSHOT_SAVED_WAITING_TOOLTIP = "✅ Take saved. Waiting for new changes."
DIRTY_EDIT_WARNING = (
    "🎿 Your current editing session hasn’t been saved.\n\n"
    "Please save this take before switching."
)

# === Snapshot Selection / Errors ===
NO_SNAPSHOT_SELECTED_TITLE = "No Take Selected"
NO_SNAPSHOT_SELECTED_MSG = "Please select a take row to load."
NO_VERSION_SELECTED_MSG = "Please select a take to continue."
NO_SELECTION_TITLE = "No Selection"
NO_SELECTION_MSG = "Please select a Take to delete."

# === Commit Errors ===
COMMIT_NOT_FOUND_TITLE = "Take Not Found"
COMMIT_NOT_FOUND_MSG = "❌ Could not find a valid Take at this row."
CANT_DELETE_ROOT_TITLE = "Can't Delete Root Take"
CANT_DELETE_ROOT_MSG = "The first Take in this Session Line can’t be removed."
DELETE_FAILED_TITLE = "Delete Failed"
DELETE_FAILED_MSG = "Could not delete this Take."
REBASE_FAILED_TITLE = "Rebase Failed"
REBASE_FAILED_MSG = "Could not rebase changes."
CHECKOUT_FAILED_TITLE = "Load Failed"
CHECKOUT_FAILED_MSG = "Could not load this Take."
COULDNT_SWITCH_TITLE = "Couldn’t Switch"
COULDNT_SWITCH_MSG = "An error occurred while switching Session Lines."
UNEXPECTED_ERROR_TITLE = "Unexpected Error"
UNEXPECTED_ERROR_MSG = "An unknown error occurred."
UNEXPECTED_ISSUE_TITLE = "Unexpected Issue"
UNEXPECTED_ISSUE_MSG = "⚠️ Something went wrong while preparing your session:\n\n{error}"
SESSION_SETUP_FAILED_MSG = "Something went wrong"
CROSS_BRANCH_COMMIT_MSG = "❌ This take is from another session line."

# === Backup / Restore ===
NO_BACKUP_FOUND_TITLE = "No Backup Found"
NO_BACKUP_FOUND_MSG = "There are no backup folders for this project."
BACKUP_RESTORED_TITLE = "Backup Restored"
BACKUP_RESTORED_MSG = "✅ Restored files from: {path}"
PROJECT_RESTORED_MSG = "✅ Session restored.\n\n🎚️ Take ID: {sha}"

# === Repo Setup / Errors ===
NO_REPO_TITLE = "🎚️ Project Not Set Up"
NO_REPO_MSG = "Please load or set up a DAW project folder before continuing."
NO_REPO_COMMIT_TITLE = "No Repo"
NO_REPO_COMMIT_MSG = "🎚️ Please initialize version control before saving your project."
NO_REPO_STATUS_LABEL = "❌ No version control repo loaded."
NO_REPO_SAVE_MSG = "🎚️ Please initialize version control before saving your project."
GIT_NOT_INITIALIZED_MSG = "⚠️ No version control initialized."
INVALID_REPO_MSG = "⚠️ Invalid repo setup."
ALREADY_ON_BRANCH_TITLE = "Already on Session Line"
ALREADY_ON_BRANCH_MSG = "🎚️ You're already on this session line:\n\n{branch}"

# === Commit Buttons ===
COMMIT_CHANGES_BTN = "🎤 Save This Take"
TAG_SNAPSHOT_BTN = "🏷️ Tag This Take"
START_NEW_VERSION_BTN = "🎼 + Alt Session"
BTN_COMMIT_NOW = "💾 Save Now"
BTN_TAG_MAIN_MIX = "🌟 Mark as Final Mix"
BTN_TAG_CREATIVE_TAKE = "🎨 Mark as Creative Version"
BTN_TAG_ALT_MIX = "🎻 Mark as Alternate Mix"
BTN_TAG_CUSTOM_LABEL = "✏️ Add Custom Tag"
BTN_LAUNCH_DAW_FILE = "🎿 Open This Take in Ableton"
BTN_OPEN_VERSION_IN_DAW = "🎿 Open This Take in DAW"
BTN_OPEN_COMMIT_PANEL = "✏️ Open Take Notes"
BTN_MAIN_MIX = "🌟 Main Mix"
BTN_CREATIVE_TAKE = "🎨 Creative"
BTN_ALT_MIX = "🎻 Alt Mix"
BTN_LOAD_SNAPSHOT = "🎿 Load This Take"
BTN_WHERE_AM_I = "📍 Where Am I?"
BTN_QUICK_SAVE = "💾 Quick Save"

# === Project Setup Buttons ===
BTN_CONNECT_REMOTE_REPO = "🔗 Connect to Remote Repo"
CONNECT_REMOTE_BTN = "🔗 Connect to Remote"
BTN_START_TRACKING = "Start Tracking"
BTN_LOAD_ALT_SESSION = "🎹 Load Alt Session"
BTN_CHANGE_PROJECT_FOLDER = "Change Project Folder"
BTN_CLEAR_SAVED_PROJECT = "Clear Saved Project"
BTN_EXPORT_SNAPSHOT = "Export Take"
BTN_IMPORT_SNAPSHOT = "Import Take"
BTN_RESTORE_BACKUP = "Restore Last Backup"
BTN_SWITCH_VERSION_LINE = "🔀 Switch Session"

# === Tooltips ===
TOOLTIP_LAUNCH_DAW_FILE = "Launch Ableton with the selected take"
TOOLTIP_LOAD_VERSION_SAFELY = "Load this take safely"
TOOLTIP_SHOW_CURRENT_VERSION = "Show current take"
TOOLTIP_SAVE_WITH_LAST_MESSAGE = "Save a take using the most recent note"
TOOLTIP_TAG_MAIN_MIX = "Tag the selected take as your Main Mix"
TOOLTIP_TAG_CREATIVE = "Tag the selected take as a Creative Version"
TOOLTIP_TAG_ALT_MIX = "Tag the selected take as an Alternate Mix"
TOOLTIP_OPEN_COMMIT_PANEL = "Open full take note editor"
TOOLTIP_OPEN_IN_FINDER = "Click to open in Finder"
TOOLTIP_START_TRACKING_FOLDER = "Start tracking the folder where your current Ableton or Logic project is saved."
TOOLTIP_SWITCH_ALT_VERSION = "Switch to a different creative version of this session"
TOOLTIP_SWITCH_BRANCH = "Switch to another creative path or saved version"
TOOLTIP_ENABLE_AUTOCOMMIT = "Enable auto-save for DAW takes"
SETUP_REMOTE_TOOLTIP = "Set up a remote Git URL (e.g. GitHub)"

# === Branch Manager ===
BRANCH_MANAGER_TITLE = "🌳 Session Lines"
SWITCH_BRANCH_BTN = "🔀 Switch Session"
NO_REPO_LOADED_MSG = "⚠️ No repo loaded."

# === Mix Tags ===
TAG_MAIN_MIX_LABEL = "Main Mix"
TAG_CREATIVE_LABEL = "Creative"
TAG_ALT_LABEL = "Alt Mix"

# === Warnings ===
UNSAVED_CHANGES_TITLE = "Unsaved Changes Detected"
UNSAVED_CHANGES_WARNING = (
    "🎿 Your latest take has unsaved edits.\n\n"
    "To keep your progress safe, please **Save This Take** "
    "or **+ Alt Session** before switching."
)
UNSAFE_DIRTY_EDITS_TITLE = "🎚️ Unsaved Session Changes Detected"
UNSAFE_DIRTY_EDITS_MSG = (
    "🎹 You’ve made changes in your DAW.\n"
    "SAVE your project in Ableton or Logic before continuing.\n\n"
    "Then click + Alt Session to capture this version.\n\n"
    "{file_list}"
)

# === Misc ===
HEADS_UP_TITLE = "Heads Up"
HEADS_UP_MSG = "Just a heads up."
NEW_PROJECT_SELECTED_MSG = "🎚️ New project selected."
TRACKING_NONE = "🎵 Tracking: None"
CURRENT_BRANCH_UNKNOWN = "🎼 No session line"
CURRENT_COMMIT_UNKNOWN = "🎙️ No take loaded"
REMOTE_ADDED_TITLE = "Remote Added"
REMOTE_ADDED_MSG = "✅ Remote 'origin' set to:\n{url}"
REMOTE_SETUP_FAILED_TITLE = "Remote Setup Failed"
REMOTE_SETUP_FAILED_MSG = "❌ Could not set up remote:\n\n{error}"
CLICK_TO_OPEN_IN_FINDER_TOOLTIP = "Click to open in Finder"

# === Status & Info ===
TAKE_LOADED_MSG = "📦 Take loaded — read-only mode"
SESSION_LINES_LOADED_MSG = "✅ {count} session lines loaded."

# === Table Headers ===
TABLE_HEADER_TAKE_ID = "Take ID"
TABLE_HEADER_SESSION_LINE = "Session Line"
TABLE_HEADER_TAKE_NOTES = "Take Notes"  # optional
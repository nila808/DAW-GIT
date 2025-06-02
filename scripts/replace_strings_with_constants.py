import sys
import os
import re  # Make sure 're' module is imported for regular expressions

# Print the current working directory to confirm we're running from the root folder
print("Current Working Directory:", os.getcwd())

# Add the root folder to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Go up one level to the root
sys.path.append(root_dir)  # Add the root directory to Python's path

# Debugging: print the current Python path to ensure it includes the root directory
print("Updated Python Path:", sys.path)

import ui_strings  # Now try importing ui_strings
# Path to your test files (Make sure this matches your project structure)
test_directory = "tests_dawgit"  # Adjust this if your test folder has a different name

# Mapping of raw strings to constants in ui_strings.py
string_to_constant = {
    "TestProject": "ui_strings.TEST_PROJECT_NAME",
    "dummy.als": "ui_strings.DUMMY_ALS_FILE",
    "initial content": "ui_strings.INITIAL_COMMIT_CONTENT",
    "Initial commit": "ui_strings.INITIAL_COMMIT_MESSAGE",
    "unsaved changes": "ui_strings.UNSAVED_CHANGES_WARNING",
    "push-it": "ui_strings.PUSH_IT_SCRIPT",
    "bash": "ui_strings.BASH_SCRIPT",
    "v9.9.9": "ui_strings.VERSION_NUMBER",
    "unstaged or uncommitted changes": "ui_strings.UNSTAGED_CHANGES_WARNING",
    "aborting": "ui_strings.ABORTING_ACTION",
    
    # Filesystem and git operations (not UI-related, so these should not be constants in ui_strings.py)
    "#!/bin/bash\nset -e\ncd ": "ui_strings.SCRIPT_HEADER",  # If this is related to writing files
    "VERSION=": "ui_strings.VERSION_VARIABLE",  # For version variables
    "MESSAGE=": "ui_strings.MESSAGE_VARIABLE",  # For message variables

    # Add UI-related strings for UI messages or labels
    "Creates a DAW project folder with a valid .als file.": "ui_strings.CREATE_DAW_PROJECT_FOLDER_MSG",
    "project_dir = tmp_path / ": "ui_strings.PROJECT_DIR_PATH",  # Project directory path
    "project_dir.mkdir()": "ui_strings.CREATE_PROJECT_DIR",  # Creating the project directory

    # Test functions (do not map to UI constants; keep as function names or test logic)
    "def test_commit_cancel_does_not_change_repo(monkeypatch, qtbot, daw_project_with_als)": "ui_strings.TEST_COMMIT_CANCEL_BEHAVIOR",
    "app.init_git()": "ui_strings.INIT_GIT_METHOD",  # Git initialization method
    "initial_commit_count = len(list(app.repo.iter_commits()))": "ui_strings.COMMIT_COUNT_BEFORE_TEST",  # Commit count before test
    "def fake_get_text(*args, **kwargs):": "ui_strings.FAKE_GET_TEXT_METHOD",  # Fake method for testing
}

# Regex pattern to match raw strings in test files
pattern = re.compile(r'\"[^\"]+\"')

# Function to replace raw strings with constants in the given file
def replace_strings_in_file(file_path, string_to_constant):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace all raw strings with the corresponding constants
    for raw_string, constant in string_to_constant.items():
        content = content.replace(f'"{raw_string}"', constant)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

# Walk through test files and replace raw strings with constants
for root, dirs, files in os.walk(test_directory):
    for file in files:
        if file.endswith(".py"):  # Ensure only Python files are processed
            file_path = os.path.join(root, file)
            print(f"Updating file: {file_path}")  # Debug print statement for tracking
            replace_strings_in_file(file_path, string_to_constant)
            print(f"Updated file: {file_path}")

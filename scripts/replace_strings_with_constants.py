import os
import re
import ui_strings  # Ensure ui_strings.py is available and properly imported

# Path to your test files (Make sure this matches your project structure)
test_directory = "tests_dawgit"  # Adjust this if your test folder has a different name

# Mapping of raw strings to constants in ui_strings.py
string_to_constant = {
    "🎧 Snapshot Mode — not on an active Version Line": "ui_strings.SNAPSHOT_DETACHED_WARNING",
    "🎧 You’re previewing an older take": "ui_strings.SNAPSHOT_SAFETY_COMMIT_MSG",
    # Add other mappings here...
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

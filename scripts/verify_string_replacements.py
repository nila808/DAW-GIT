import os
import re
import ui_strings  # Make sure ui_strings.py is in the same directory or accessible in your PYTHONPATH

# Path to your test files
test_directory = "tests_dawgit"

# Mapping of raw strings to constants in ui_strings.py
string_to_constant = {
    "🎧 Snapshot Mode — not on an active Version Line": "ui_strings.SNAPSHOT_DETACHED_WARNING",
    "🎧 You’re previewing an older take": "ui_strings.SNAPSHOT_SAFETY_COMMIT_MSG",
    # Add other mappings here...
}

# Regex pattern to match raw strings in test files
pattern = re.compile(r'\"[^\"]+\"')

# Get all raw strings from the test files
def get_all_raw_strings(test_directory):
    raw_strings = []
    for root, dirs, files in os.walk(test_directory):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    found_strings = pattern.findall(content)
                    raw_strings.extend(found_strings)
    return raw_strings

# Function to verify that all raw strings are replaced with constants
def test_no_raw_strings_left():
    raw_strings = get_all_raw_strings(test_directory)  # Get all raw strings
    for raw_string in raw_strings:
        if raw_string not in string_to_constant:
            print(f"Missing constant for string: {raw_string}")  # If a raw string isn't mapped, print it

# Function to verify that constants are defined in ui_strings.py
def test_constants_existence():
    for constant in string_to_constant.values():
        if constant not in dir(ui_strings):
            print(f"Constant {constant} does not exist in ui_strings")

# Run the verification tests
test_no_raw_strings_left()  # Check for any raw strings that aren't replaced
test_constants_existence()  # Ensure constants are defined in ui_strings.py

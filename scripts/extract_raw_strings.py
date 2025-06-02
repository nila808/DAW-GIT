import os
import re

# Path to your test files
test_directory = "tests_dawgit"  # Change this to match your actual test directory

# Regex pattern to match raw strings in the test files
pattern = re.compile(r'\"[^\"]+\"')

# Store the strings found
raw_strings = []

# Function to extract raw strings from the test files
def extract_raw_strings(test_directory):
    raw_strings = []
    for root, dirs, files in os.walk(test_directory):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    found_strings = pattern.findall(content)
                    raw_strings.extend(found_strings)
    return raw_strings

# Get all raw strings from test files
raw_strings = extract_raw_strings(test_directory)

# Output the raw strings found
print(f"Found {len(raw_strings)} raw strings.")
for string in raw_strings:
    print(f"Raw string: {string}")

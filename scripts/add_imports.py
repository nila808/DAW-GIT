import os

# Path to your test files
test_directory = "../tests_dawgit"  # Adjust this to point to the tests folder from the scripts folder

# The import line to add
import_line = "import ui_strings\n"

# Function to add import to the top of the file if it's not already there
def add_import_to_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Check if the import is already present
    if not any(line.strip() == import_line.strip() for line in lines):
        # Add the import at the top
        lines.insert(0, import_line)

        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)
            print(f"Import added to: {file_path}")  # Debugging print

# Walk through all Python files in the test directory and add the import
for root, dirs, files in os.walk(test_directory):
    for file in files:
        if file.endswith(".py"):  # Ensure only Python files are processed
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")  # Debugging print to show which files are being processed
            add_import_to_file(file_path)

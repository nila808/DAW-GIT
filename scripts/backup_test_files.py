import shutil
import os

# Path to your test files
test_directory = "tests_dawgit"

# Backup function to save original files with a .bak extension
def backup_file(file_path):
    backup_path = file_path + ".bak"
    shutil.copy(file_path, backup_path)
    print(f"Backup created for: {file_path}")

# Backup all test files
for root, dirs, files in os.walk(test_directory):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            backup_file(file_path)

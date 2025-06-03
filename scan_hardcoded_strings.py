import re
from pathlib import Path

def scan_for_hardcoded_strings():
    project_path = Path('.')
    ui_strings_file = project_path / 'ui_strings.py'

    with open(ui_strings_file, 'r') as f:
        ui_constants = set(re.findall(r'^([A-Z_]+)\s?=', f.read(), re.MULTILINE))

    hardcoded_found = {}

    

    py_files = project_path.rglob('*.py')
    for py_file in py_files:
        if py_file.name == 'ui_strings.py':
            continue

        content = py_file.read_text()

        # Check common UI string locations
        patterns = [
            r'QMessageBox\.\w+\((?:self,)?\s*"(.*?)"',  # QMessageBox
            r'setText\("(.*?)"\)',                      # QLabel.setText()
            r'setToolTip\("(.*?)"\)',                   # Widget tooltips
            r'QInputDialog\.getText\([^,]+,\s*"(.*?)"', # Input dialogs
            r'QPushButton\("(.*?)"\)'                   # Button labels
        ]

        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, content))

        filtered = [m for m in matches if not any(const_value in m for const_value in ui_constants)]
        if filtered:
            hardcoded_found[py_file.name] = filtered

    return hardcoded_found

results = scan_for_hardcoded_strings()

if results:
    print("🔴 Hardcoded strings found:")
    for file, strings in results.items():
        print(f"\n{file}:")
        for s in strings:
            print(f" - {s}")
else:
    print("✅ No hardcoded strings found!")

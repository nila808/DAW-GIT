import os
import re
import pytest
from pathlib import Path

# Path to the ui_strings.py constants file
UI_STRINGS_FILE = Path(__file__).parent.parent / "ui_strings.py"
TESTS_DIR = Path(__file__).parent

@pytest.fixture(scope="module")
def ui_constants():
    pattern = re.compile(r'^([A-Z_]+)\s*=\s*(["\'])(.*?)\2', re.MULTILINE)
    with open(UI_STRINGS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    matches = pattern.findall(content)
    return set(m[2] for m in matches)


def get_literal_strings(code):
    # Find all literal strings in code
    return re.findall(r'(?<!from ui_strings import )["\'](.*?[^\\])["\']', code)


@pytest.mark.parametrize("file_path", list(TESTS_DIR.glob("test_*.py")))
def test_ui_strings_in_tests_use_constants(file_path, ui_constants):
    with open(file_path, "r") as f:
        code = f.read()

    # Skip this file itself to avoid false positives
    if "test_no_raw_ui_strings_in_tests" in file_path.name:
        return

    strings = get_literal_strings(code)
    flagged = []

    for s in strings:
        if (
            len(s.strip()) >= 6
            and any(c in s for c in ("🎧", "🎿", "🎼", "❌", "✅", "🔀", "🔗", "📍"))
            and not any(ui_string in s for ui_string in ui_constants)
        ):
            flagged.append(s)

    assert not flagged, f"{file_path.name} contains hardcoded UI strings: {flagged}"

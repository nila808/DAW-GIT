import re
import pytest
from pathlib import Path

@pytest.fixture
def ui_strings_text():
    ui_path = Path(__file__).resolve().parent.parent / "ui_strings.py"
    assert ui_path.exists(), "ui_strings.py not found"
    return ui_path.read_text(encoding="utf-8")

def test_no_duplicate_keys(ui_strings_text):
    pattern = re.compile(r"^([A-Z0-9_]+)\s*=\s*([\"'])(.*?)(?<!\\)\2$", re.MULTILINE)
    matches = pattern.findall(ui_strings_text)

    keys_seen = {}
    duplicates = []

    for key, _, value in matches:
        if key in keys_seen:
            duplicates.append(key)
        keys_seen[key] = value

    assert not duplicates, f"Duplicate string keys found: {duplicates}"

def test_no_empty_values(ui_strings_text):
    pattern = re.compile(r"^([A-Z0-9_]+)\s*=\s*([\"'])(.*?)(?<!\\)\2$", re.MULTILINE)
    matches = pattern.findall(ui_strings_text)

    empty_keys = [key for key, _, value in matches if value.strip() == ""]
    assert not empty_keys, f"Empty UI string values found: {empty_keys}"


def test_all_ui_strings_used(ui_strings_text):
    # Extract all string keys from ui_strings.py
    pattern = re.compile(r"^([A-Z0-9_]+)\s*=\s*([\"'])", re.MULTILINE)
    keys = [match.group(1) for match in pattern.finditer(ui_strings_text)]

    # Scan all project .py files for usage
    project_root = Path(__file__).resolve().parent.parent
    source_files = list(project_root.glob("**/*.py"))
    used_keys = set()

    for file in source_files:
        if file.name == "ui_strings.py":
            continue
        content = file.read_text(encoding="utf-8", errors="ignore")
        for key in keys:
            if key in content:
                used_keys.add(key)

    unused_keys = sorted(set(keys) - used_keys)
    assert not unused_keys, f"The following UI strings are not used anywhere: {unused_keys}"

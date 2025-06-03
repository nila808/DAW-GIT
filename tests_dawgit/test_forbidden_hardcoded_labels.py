from ui_strings import ROLE_LABEL_MAP
from pathlib import Path
import pytest

FORBIDDEN_UI_STRINGS = list(ROLE_LABEL_MAP.values())

def test_no_hardcoded_role_labels():
    project_root = Path(__file__).resolve().parents[1]
    offending = {}

    for py_file in project_root.rglob("*.py"):
        if (
            "ui_strings.py" in py_file.name or
            "site-packages" in str(py_file) or
            "daw-git-env" in str(py_file) or
            "scripts/prep_release.py" in str(py_file)
        ):
            continue

        content = py_file.read_text()
        # Remove comments to prevent false positives from commented-out lines
        lines = content.splitlines()
        non_comment_lines = [line for line in lines if not line.strip().startswith("#")]
        cleaned_content = "\n".join(non_comment_lines)
        found = [s for s in FORBIDDEN_UI_STRINGS if s in cleaned_content]


        if found:
            offending[str(py_file)] = found

    if offending:
        msg = "\n".join(f"{file}: {', '.join(strings)}" for file, strings in offending.items())
        pytest.fail(f"❌ Forbidden hardcoded role labels found:\n{msg}")


# to run use:             tests_dawgit/test_forbidden_hardcoded_labels.py
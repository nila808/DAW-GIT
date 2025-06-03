import ui_strings
import os
import subprocess
from pathlib import Path
from git import Repo
from ui_strings import (
    PUSH_USAGE_MSG,
    PUSH_INVALID_TAG_MSG,
    PUSH_TAG_EXISTS_MSG,
    PUSH_ABORT_DIRTY_MSG,
    PUSH_WILL_RUN_TESTS_MSG
)

def test_push_it_aborts_on_unstaged_changes(tmp_path):
    # Setup a fake Git repo
    repo_path = tmp_path / ui_strings.TEST_PROJECT_NAME
    repo_path.mkdir()
    repo = Repo.init(repo_path)

    # Add a dummy file and commit
    file = repo_path / ui_strings.DUMMY_ALS_FILE
    file.write_text(ui_strings.INITIAL_COMMIT_CONTENT)
    repo.index.add([str(file)])
    repo.index.commit(ui_strings.INITIAL_COMMIT_MESSAGE)

    # Modify the file without staging it
    file.write_text(ui_strings.UNSAVED_CHANGES_WARNING)

    # Define the content of the push-it script
    PUSH_IT_SCRIPT = f"""#!/bin/bash
    set -e
    cd $(git rev-parse --show-toplevel)
    VERSION="$1"
    MESSAGE="$2"

    if [[ -z "$VERSION" ]]; then echo "{ui_strings.PUSH_USAGE_MSG}"; exit 1; fi
    if ! [[ "$VERSION" =~ ^[a-zA-Z0-9._-]+$ ]]; then echo "{ui_strings.PUSH_INVALID_TAG_MSG}"; exit 1; fi
    if git rev-parse "$VERSION" >/dev/null 2>&1; then echo "{ui_strings.PUSH_TAG_EXISTS_MSG}"; exit 1; fi

    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "{ui_strings.UNSAVED_CHANGES_WARNING}"
        echo "{ui_strings.PUSH_ABORT_DIRTY_MSG}"
        exit 1
    fi

    echo "{ui_strings.PUSH_WILL_RUN_TESTS_MSG}"
    """

    # Save the push-it script to the temp dir
    push_it_script = repo_path / "push_it_script.sh"  # Make sure this is a valid file name
    
    # Ensure the parent directory exists
    push_it_script.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if they don't exist
    
    # Write the content to the script file
    push_it_script.write_text(PUSH_IT_SCRIPT)

    # Change permissions to make the script executable
    push_it_script.chmod(0o755)

    # Run the script and capture output
    result = subprocess.run(
        [ui_strings.BASH_SCRIPT, str(push_it_script), ui_strings.VERSION_NUMBER],
        cwd=repo_path,
        text=True,
        capture_output=True
    )

    # Assert it exits with an error and includes expected messages
    assert result.returncode != 0
    assert ui_strings.UNSAVED_CHANGES_WARNING.lower() in result.stdout.lower()
    assert ui_strings.ABORTING_ACTION.lower() in result.stdout.lower()  # Case-insensitive check

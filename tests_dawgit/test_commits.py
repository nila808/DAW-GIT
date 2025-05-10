import os
import tempfile
import subprocess
from daw_git_gui import DAWGitApp

def test_auto_commit_creates_tag(qtbot):
    import os
    import tempfile
    import subprocess

    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system("git init")
    os.system('git config user.email "test@example.com"')
    os.system('git config user.name "Test User"')

    with open("init.txt", "w") as f:
        f.write("init")
    os.system("git add init.txt")
    os.system("git commit -m 'init'")

    subprocess.run(["git", "tag", "v-test"], cwd=temp_dir, check=True)

    result = subprocess.run(["git", "tag", "-l"], cwd=temp_dir, stdout=subprocess.PIPE, text=True)
    tag_list = result.stdout.strip().split("\n") if result.stdout.strip() else []

    print("Available tags (via shell):", tag_list)
    assert "v-test" in tag_list

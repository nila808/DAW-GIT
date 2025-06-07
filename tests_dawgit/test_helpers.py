# tests_dawgit/test_helpers.py

import os
import uuid
from pathlib import Path
from git import Repo
import tempfile
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def working_directory(path):
    prev_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_dir)

def create_test_project(tmp_path=None):
    if tmp_path is None:
        tmp_path = Path(tempfile.mkdtemp())

    project_path = tmp_path.resolve() / "project"
    project_path.mkdir(parents=True, exist_ok=True)

    repo = Repo.init(project_path)
    daw_file = project_path / "track.als"
    daw_file.write_text("init")

    with working_directory(project_path):
        repo.index.add([str(daw_file.relative_to(project_path))])
        repo.index.commit("init")

    return project_path, repo
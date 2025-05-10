# DAWGitApp Test Manual

This guide explains how to run and write tests for DAWGitApp.

---

## 🚀 Run Tests from Terminal

From project root:
```bash
./run_tests.sh
```

Or manually:
```bash
source daw-git-env/bin/activate
pytest -v tests_dawgit/
```

---

## 🧪 PyCharm Setup

1. Go to `Preferences > Python Interpreter` and select your virtualenv
2. Add a pytest run config:
   - Target: `tests_dawgit/`
   - Working Dir: project root
   - Environment: make sure `daw-git-env` is activated

3. You can now run tests via the UI or Ctrl+Shift+R.

---

## 📂 tests_dawgit/

Contains:
- `test_commits.py` — tag creation, auto commit
- `test_repo_setup.py` — git init, folder detection
- `test_ui_logic.py` — window title
- `test_path_handling.py` — config load/save
- `conftest.py` — reusable fixtures

---

## 🧹 Cleanup

Use `cleanup_temp_test_folders.sh` to remove temp folders older than 1 hour.

```bash
chmod +x cleanup_temp_test_folders.sh
./cleanup_temp_test_folders.sh
```

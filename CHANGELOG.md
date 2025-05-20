

## [v1.0.3-testpass] – 2025-05-21
**Author:** @niccavendish
- ⏳ Placeholder entry


## [head -n 10 CHANGELOG.md] – 2025-05-21
**Author:** @niccavendish
- ⏳ Placeholder entry
# 🎼 DAWGitApp – Changelog

## [v1.0.3-testpass] – 2025-05-21  
**Author:** @nila808

### ✅ Full Test Suite Passing
- 🟢 83/83 unit and integration tests passing  
- 🧪 1 full end-to-end flow verified (`test_daw_git_end_to_end`)  
- ✅ No skipped, xfailed, or unstable tests remain

### 🔧 Key Fixes
- Fixed `commit_changes()` to safely handle missing `repo` or `project_path`
- Hardened `load_commit_roles()` to skip when `project_path is None`
- Normalized newline-stripped Git commit message assertions
- Improved error messaging on failed commits due to invalid state
- Validated and cleaned modal feedback and label state updates

### 🧪 Test Improvements
- Injected `.als`/`.logicx` file diffs into snapshot commit tests to force real Git commits
- Expanded snapshot and commit UI feedback tests to verify modal text and label accuracy
- Patched first-time launch logic for welcome modal display and safe startup
- Fully covered edge cases involving no project loaded, detached HEADs, and dummy test modes

### 🧼 Final Cleanup
- All temp paths cleaned via test teardown
- `.dawgit_roles.json` safely bypassed in test mode if project path is unset
- Tests now run cleanly on both first-time and repeat launches

📌 **Status:** Test suite stable.  
🧪 **Next:** Manual UI walkthrough & final QA.


## v1.0.3 – Commit Role Test Coverage
**Date:** 2025-05-18  
**Author:** @nila808  

### ✅ Added
- AT-050 / MT-029 – Tag commit as "Main Mix"
- AT-051 / MT-031 – Re-tag commit from one role to another
- AT-052 / MT-032 – Switch to "Creative Take" commit
- AT-053 / MT-033 – Switch to "Alt Mixdown" commit
- AT-054 / MT-034 – Tag/untag repeatedly
- AT-055 / MT-035 – Delete commit with role and verify cleanup

### 🧪 Tests
All added to: `tests_dawgit/test_commit_role_persistence.py`

### 🔧 Notes
- `assign_commit_role()` now properly saves and commits `.dawgit_roles.json`
- `tag_main_mix()` patched for test mode execution

---

## [v1.0.2-testpass] — 2025-05-20

### ✅ Test Suite Stability
- Achieved 100% passing test coverage across 60 automated tests, including:
  - Safety logic
  - Role tagging
  - Branch switching
  - Snapshot checkouts
  - DAW launch behavior

### 🔧 Fixes & Improvements
- Fixed `open_latest_daw_project()` logic to:
  - Properly return mocked file in test mode
  - Bypass snapshot confirmation during tests
  - Skip launching placeholder/test files safely
- Removed old `mock.MagicMock` return shortcut
- Ensured `.als` detection and file sorting consistent across test + real mode

### 🧪 Test Tools
- Added `run_failures_only.sh`: logs test output and copies FAILURES block to clipboard for fast triage
- `run_tests.sh` now detects and reports failures with improved feedback

### 🧼 Cleanup
- Removed stale shortcut logic
- Ensured detached HEAD logic and launch conditions are test-safe
- Pushed tag `v1.0.2-testpass` to mark this fully passing milestone

---

## [v1.0.2-rolepass] – 2025-05-19

✅ Full test suite passing (54/54)  
🆕 Added commit role tagging system (Main Mix, Creative Take, Alt Mixdown)  
🎼 Roles persist across app restarts via `.dawgit_roles.json`  
🎛 UI buttons for role tagging implemented and tested  
🧪 8 new role-tagging tests: persistence, retagging, multiple commits  
🔐 All safety layers verified (unsaved changes, detached HEAD, clean checkouts)  
🎯 All Git branch and commit operations tested  
🧼 Final cleanup & regression-proofed end-to-end workflow  

Stable milestone tagged as `v1.0.2-rolepass`

---

## [v1.x.x] – [Release Date]

✅ Full test suite passing  
🆕 New features: [brief summary of added features]  
🔧 Bug fixes: [summarize any fixes]  
🔐 Security: [mention any security-related fixes or enhancements]  
🔄 Other changes: [mention other changes made]  


## [Unreleased]
- ⏳ Placeholder for next release

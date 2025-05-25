def test_remote_connect_push(monkeypatch, tmp_path):
    from daw_git_gui import DAWGitApp
    import subprocess

    repo = subprocess.run(["git", "init"], cwd=tmp_path, check=True)
    (tmp_path / "test.als").write_text("Ableton data")
    subprocess.run(["git", "add", "."], cwd=tmp_path)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path)

    app = DAWGitApp(project_path=str(tmp_path), build_ui=False)

    # Patch dialog to auto-fill remote URL and confirm
    monkeypatch.setattr("PyQt6.QtWidgets.QInputDialog.getText", lambda *a, **kw: ("https://github.com/your-user/your-test-repo.git", True))

    # Run remote connect
    app.connect_to_remote_repo()

    assert "origin" in [r.name for r in app.repo.remotes]

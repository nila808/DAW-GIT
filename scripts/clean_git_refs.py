#!/usr/bin/env python3

import os
import re
from pathlib import Path

def is_bad_ref(ref_path):
    return " " in ref_path or not re.match(r'^[a-f0-9]{7,40}$', ref_path.stem)

def clean_git_refs(git_dir=".git"):
    print("🔍 Scanning for malformed Git refs...")

    ref_paths = list(Path(git_dir).rglob("*"))
    deleted = []

    for path in ref_paths:
        if path.is_file() and "refs/heads" in str(path):
            if is_bad_ref(path):
                print(f"❌ Removing bad ref: {path}")
                path.unlink()
                deleted.append(str(path))

    packed_refs = Path(git_dir) / "packed-refs"
    if packed_refs.exists():
        content = packed_refs.read_text()
        lines = content.splitlines()
        cleaned_lines = [
            line for line in lines
            if not ("test branch" in line or re.search(r'refs/heads/.*\s', line))
        ]
        if len(cleaned_lines) < len(lines):
            print("🧼 Cleaning packed-refs...")
            packed_refs.write_text("\n".join(cleaned_lines) + "\n")

    print(f"✅ Done. {len(deleted)} file refs deleted.")

if __name__ == "__main__":
    if os.getenv("DAWGIT_TEST_MODE") == "1":
        clean_git_refs()
    else:
        print("🛑 Skipping: only runs in test mode (set DAWGIT_TEST_MODE=1)")

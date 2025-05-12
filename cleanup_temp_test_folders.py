import os
import tempfile
import shutil
import time

def cleanup_temp_dirs(age_minutes=60):
    base_temp = tempfile.gettempdir()
    now = time.time()
    removed = 0

    for name in os.listdir(base_temp):
        path = os.path.join(base_temp, name)
        try:
            if os.path.isdir(path) and name.startswith("tmp"):
                age_sec = now - os.path.getmtime(path)
                if age_sec > age_minutes * 60:
                    shutil.rmtree(path)
                    print(f"🗑️ Removed: {path}")
                    removed += 1
        except Exception as e:
            print(f"⚠️ Skipped {path}: {e}")

    print(f"✅ Cleanup complete. {removed} temp folders removed.")

if __name__ == "__main__":
    cleanup_temp_dirs()

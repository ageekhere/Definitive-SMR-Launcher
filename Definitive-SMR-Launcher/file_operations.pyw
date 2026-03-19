"""
file_operations.py

Contains utility functions for copying files to the game directory.
"""

import __main__  # Access global variables from main
import hashlib

def file_hash(path):
    """Return SHA256 hash of a file."""
    if not __main__.os.path.exists(path):
        return None

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def file_operations(file_name="file1.exe") -> bool:
    """
    Copy a file from 'exe/' folder to the game path (__main__.gGamePath) and verify it exists.
    Skips copy if file already matches.
    """

    source_path = __main__.os.path.join(__main__.os.getcwd(), "exe", file_name)
    dest_path = __main__.os.path.join(__main__.gGamePath, file_name)

    # Check if source exists
    if not __main__.os.path.exists(source_path):
        __main__.error_logs(f"[file_operations] Source file not found: {source_path}", "error")
        return False

    try:
        # 🔍 Compare hashes if destination exists
        if __main__.os.path.exists(dest_path):
            src_hash = file_hash(source_path)
            dst_hash = file_hash(dest_path)

            if src_hash == dst_hash:
                __main__.error_logs(
                    f"[file_operations] {file_name} already up-to-date, skipping copy","info")
                return True

        # 📦 Copy if different or missing
        __main__.shutil.copy(source_path, dest_path)
        __main__.error_logs(f"[file_operations] Copied {file_name} to {__main__.gGamePath}", "info")

    except Exception as e:
        __main__.error_logs(f"[file_operations] Error copying file {file_name}: {e}", "error")
        return False

    # ✅ Verify destination
    if __main__.os.path.exists(dest_path):
        __main__.error_logs(f"[file_operations] File successfully exists at destination: {dest_path}", "info")
        return True
    else:
        __main__.error_logs(f"[file_operations] File copy failed for {file_name}", "error")
        return False
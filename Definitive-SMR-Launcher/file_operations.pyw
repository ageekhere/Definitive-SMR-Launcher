"""
file_operations.py

Contains utility functions for copying files to the game directory.
"""

import __main__  # Access global variables from main

def file_operations(file_name="file1.exe") -> bool:
    """
    Copy a file from 'exe/' folder to the game path (__main__.gGamePath) and verify it exists.

    Args:
        file_name (str): Name of the file to copy.

    Returns:
        bool: True if copy succeeded and file exists at destination, False otherwise.
    """
    source_path = __main__.os.path.join(__main__.os.getcwd(), "exe", file_name)
    dest_path = __main__.os.path.join(__main__.gGamePath, file_name)

    # Check if source exists
    if not __main__.os.path.exists(source_path):
        __main__.error_logs(f"[file_operations] Source file not found: {source_path}", "error")
        return False

    try:
        __main__.shutil.copy(source_path, dest_path)
        __main__.error_logs(f"[file_operations] Copied {file_name} to {__main__.gGamePath}", "info")
    except Exception as e:
        __main__.error_logs(f"[file_operations] Error copying file {file_name}: {e}", "error")
        return False

    # Verify destination
    if __main__.os.path.exists(dest_path):
        __main__.error_logs(f"[file_operations] File successfully exists at destination: {dest_path}", "info")
        return True
    else:
        __main__.error_logs(f"[file_operations] File copy failed for {file_name}", "error")
        return False
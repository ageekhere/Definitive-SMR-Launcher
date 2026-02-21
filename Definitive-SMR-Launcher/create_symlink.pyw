"""
create_symlink.py

Provides a utility function to create symbolic links safely,
using globals and imports from main.py.
"""
import os
from error_logs import error_logs 

def create_symlink(source_dir: str, target_dir: str, target_is_directory: bool):
    """
    Create a symbolic link from source_dir pointing to target_dir.

    Parameters:
        source_dir (str): The path where the symlink will be created.
        target_dir (str): The target path the symlink points to.
        target_is_directory (bool): True if the target is a directory, False if a file.

    Notes:
        Uses __main__.os.symlink and __main__.debug.
        Any OSError is caught and logged using debug.
    """
    try:
        os.symlink(target_dir, source_dir, target_is_directory)
        error_logs(f"[create_symlink] Symlink created: {source_dir} -> {target_dir}", "info")
    except OSError as e:
        error_logs(f"[create_symlink] Error creating symlink {source_dir} -> {target_dir}: {e}", "error")
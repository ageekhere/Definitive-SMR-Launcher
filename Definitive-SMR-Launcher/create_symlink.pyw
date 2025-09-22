"""
create_symlink.py

Provides a utility function to create symbolic links safely,
using globals and imports from main.py.
"""
import __main__ # Access globals and imported modules

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
        __main__.os.symlink(target_dir, source_dir, target_is_directory)
        __main__.error_logs(f"[create_symlink] Symlink created: {source_dir} -> {target_dir}", "info")
    except OSError as e:
        __main__.error_logs(f"[create_symlink] Error creating symlink {source_dir} -> {target_dir}: {e}", "error")
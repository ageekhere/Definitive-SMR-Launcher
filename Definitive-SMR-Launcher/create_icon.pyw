import os
import sys
from error_logs import error_logs
def create_icon(sys,window):
    """
    Set the window icon depending on execution context.
    
    - If frozen (PyInstaller bundle), loads from sys._MEIPASS (temp extraction folder).
    - Otherwise, loads from local path (icon/icon.ico).
    """
    try:
        if getattr(sys, "frozen", False):  # Running as a PyInstaller bundle
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            error_logs(f"[create_icon] Using bundled icon at {icon_path}", "info")
        else:  # Running as normal Python script
            icon_path = os.path.join("icon", "icon.ico")
            error_logs(f"[create_icon] Using script icon at {icon_path}", "info")

        window.after(200, lambda: window.iconbitmap(icon_path))
        error_logs("[create_icon] Successfully applied icon", "info")

    except Exception as e:
        error_logs("[create_icon] Failed to set icon: " + str(e), "error")
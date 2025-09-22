"""
icon_manager.pyw

Handles application icon setup for both PyInstaller bundles and normal Python scripts.
Uses globals from __main__ (expects gApp).
"""
import __main__  # Access globals from the main script
def create_icon(sys):
    """
    Set the window icon depending on execution context.
    
    - If frozen (PyInstaller bundle), loads from sys._MEIPASS (temp extraction folder).
    - Otherwise, loads from local path (icon/icon.ico).
    """

    try:
        if getattr(sys, "frozen", False):  # Running as a PyInstaller bundle
            icon_path = __main__.os.path.join(sys._MEIPASS, "icon.ico")
            __main__.error_logs(f"[create_icon] Using bundled icon at {icon_path}", "info")
        else:  # Running as normal Python script
            icon_path = __main__.os.path.join("icon", "icon.ico")
            __main__.error_logs(f"[create_icon] Using script icon at {icon_path}", "info")

        __main__.gApp.iconbitmap(icon_path)
        __main__.error_logs(f"[create_icon] Successfully applied icon", "info")

    except Exception as e:
        __main__.error_logs(f"[create_icon] Failed to set icon: {e}", "error")
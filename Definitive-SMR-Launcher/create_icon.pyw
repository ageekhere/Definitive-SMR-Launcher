import __main__ # Import the __main__ module so we can access variables and functions defined in the main script
def create_icon(sys,window):
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

        window.after(200, lambda: window.iconbitmap(icon_path))
        #window.iconbitmap(icon_path)
        __main__.error_logs("[create_icon] Successfully applied icon", "info")

    except Exception as e:
        __main__.error_logs("[create_icon] Failed to set icon: " + str(e), "error")
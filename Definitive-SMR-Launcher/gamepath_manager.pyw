"""
gamepath_manager.py

Handles the "Set Game Path" button logic.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports
def gamepath_manager():
    """
    Open a folder selection dialog to set the game's installation path.
    Updates global variables, labels, and config using get_config_value / set_config_value.
    """
    try:
        folder_path = __main__.filedialog.askdirectory()
        if folder_path:
            # Normalize path for Windows-style backslashes
            folder_path = __main__.os.path.normpath(folder_path)

            # Update label in UI
            __main__.gGameLocation_label.configure(
                text=str(__main__.string_utils(folder_path, max_length=30, placeholder="..."))
            )

            # Update global variables
            __main__.gGamePath = folder_path

            # Update config using the new helper
            __main__.set_config_value("gamepath", folder_path)

            # Enable buttons if path is valid
            if __main__.gGamePath != "":
                __main__.gStart_button.configure(state="normal")
                __main__.gGameTypeDrop.configure(state="normal")
                __main__.gCustom_exe_button.configure(state="normal")
                __main__.gCustom_levels_button.configure(state="normal")
                
            __main__.error_logs(f"[gamepath_manager] Game parth set " + str(folder_path), "info")
    except Exception as e:
        __main__.error_logs(f"[gamepath_manager] Error setting game path: {e}", "error")
"""
map_info_manager.py

Provides a popup window to display map information.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports

def map_info_manager(mapId: str):
    """
    Display the content of a mapInfo.txt file in a popup CTk window.

    Parameters:
        mapId (str): The folder name of the map.
    
    Uses:
        __main__.ctk: CustomTkinter for GUI elements.
        __main__.os: For building paths.
    """
    try:
        __main__.error_logs(f"[map_info_manager] Loading map info", "info")
        target_path = __main__.os.path.join(str(__main__.os.getcwd()), "maps", mapId, "mapInfo.txt")
        
        with open(target_path, "r", encoding="utf-8") as f:
            map_info_text = f.read()

        # Create a top-level popup window
        popup = __main__.ctk.CTkToplevel()
        popup.title("Map Information")

        # Set size
        width, height = 800, 600 
        popup.geometry(f"{width}x{height}")

        # Keep popup always on top
        popup.attributes("-topmost", True)

        # Center relative to main window
        master = popup.master
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2 - width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2 - height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        # Create textbox
        textbox = __main__.ctk.CTkTextbox(
            popup,
            width=780,
            height=580,
            wrap="word"
        )
        textbox.pack(pady=20, padx=20)

        # Insert text and make read-only
        textbox.insert("1.0", map_info_text)
        textbox.configure(state="disabled")

    except FileNotFoundError:
        __main__.error_logs(f"[map_info_manager] Map info file not found for {mapId}", "error")
    except Exception as e:
        __main__.error_logs(f"[map_info_manager] Error displaying map info for {mapId}: {e}", "error")
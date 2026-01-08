"""
map_info_manager.py

Provides a popup window to display map information.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports
import webbrowser

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
        __main__.error_logs("[map_info_manager] Loading map info", "info")
        target_path = __main__.os.path.join(str(__main__.os.getcwd()), "maps", mapId, "mapInfo.txt")
        
        with open(target_path, "r", encoding="utf-8") as f:
            map_info_text = f.read()

        # Create a top-level popup window
        popup = __main__.ctk.CTkToplevel(__main__.gApp)
        #if mapId in __main__.gUnstable_list:
        if __main__.get_map_data(mapId, __main__.gMap_rating_matrix,"is_stable") == "n":
            popup.title("Map Information - " + str(mapId + " (Unstable Map, Try With Lowest Graphic Settings)" ))
        else:
            popup.title("Map Information - " + str(mapId))

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

        __main__.create_icon(__main__.sys, popup)

        def rate_map(map:str):
            if map == "":
                return
            url = "https://github.com/ageekhere/Definitive-SMR-Launcher/discussions/" + str(map)
            webbrowser.open(url)
        
        btn_text = str(__main__.rating_check(mapId))

        map_url = __main__.get_map_data(mapId, __main__.gMap_rating_matrix,"url")
        btn_font = __main__.ctk.CTkFont(size=16)
        info_btn = __main__.ctk.CTkButton(
            popup,
            width=100,
            height=20,
            corner_radius=0,
            text= btn_text + " Click Here to rate Map",
            font=btn_font,
            command=__main__.partial(rate_map, map_url))
        info_btn.grid(row=1, column=0, padx=5, pady=0,sticky="nw")

        if(btn_text == "Rating Unavailable"):
            
            info_btn.configure(text=btn_text)
            info_btn.configure(state="disabled")

        # Create textbox
        textbox = __main__.ctk.CTkTextbox(
            popup,
            width=780,
            height=520,
            wrap="word"
        )
        #textbox.pack(pady=20, padx=20)
        textbox.grid(row=1, column=0, padx=5, pady=30,sticky="n")

        # Insert text and make read-only
        textbox.insert("1.0", map_info_text)
        textbox.configure(state="disabled")

    except FileNotFoundError:
        __main__.error_logs(f"[map_info_manager] Map info file not found for {mapId}", "error")
    except Exception as e:
        __main__.error_logs(f"[map_info_manager] Error displaying map info for {mapId}: {e}", "error")
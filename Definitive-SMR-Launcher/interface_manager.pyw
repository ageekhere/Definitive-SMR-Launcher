"""
interface_manager.py

Creates the main GUI interface components for the launcher.
"""

import __main__
def unload_map():
    __main__.gSelected_button = getattr(__main__, "gSelected_button", None)
    if __main__.gSelected_button != None:
        __main__.gSelected_button.configure(fg_color="transparent")
        __main__.gSelected_button.configure(border_width=0)

    for path in __main__.gGameDocs.rglob("*"):
        if path.is_symlink():
            __main__.error_logs(f"Removing symlink: {path}", "info")
            path.unlink()
            __main__.gRemoveSymlink.configure(state="disabled")

def interface_manager(os,ctk):
    __main__.error_logs("[interface] Setting up interface", "info")
    __main__.gLog_button = ctk.CTkButton(__main__.gApp, text="Logs", corner_radius=0, command=__main__.debug_window, width=40) # Logs Button
    __main__.gStart_button = ctk.CTkButton(__main__.gApp, text="Start Game", command=__main__.game_launcher, corner_radius=0) # Start Game Button
    __main__.gGamepath_button = ctk.CTkButton(__main__.gApp, text="Set Game Path: ", corner_radius=0, command=__main__.gamepath_manager) # Set Game Path Button
    __main__.gUpdate_maps_button = ctk.CTkButton(__main__.gApp, text="Maps Available ", corner_radius=0,fg_color="green", command=__main__.map_updater) # Update Maps Button
    __main__.gGameLocation_label = ctk.CTkLabel(__main__.gApp, text="Game Path:") # Game Path Label

    __main__.gRemoveSymlink = ctk.CTkButton(__main__.gApp, text="Unload Map", corner_radius=0, command=unload_map) # Update Maps Button
    
    unload_map()


    # Custom Difficulty CTkCheckBox
    __main__.gCustom_difficulty = ctk.IntVar(value=int(__main__.get_config_value("customdifficulty", default="0")))
    __main__.gCustom_levels_button = ctk.CTkCheckBox(
        __main__.gApp,
        text="Custom Difficulty Levels  ",
        variable=__main__.gCustom_difficulty,
        corner_radius=0,
        command=__main__.difficulty_manager
    )

    # Check XML file for difficulty if exists
    if __main__.gGamePath != "":
        difficulty_path = __main__.os.path.join(__main__.gGamePath, "Assets", "XML", "RRT_Difficulty.xml")
        if __main__.os.path.exists(difficulty_path):
            __main__.error_logs("[interface] Loading Difficulty settings", "info")
            size_bytes = __main__.os.path.getsize(difficulty_path)
            __main__.gCustom_difficulty.set(1 if size_bytes > 7000 else 0)
        else:
            __main__.gCustom_difficulty.set(0)
            __main__.error_logs(f"[interface] File does not exist: {difficulty_path}", "warning")

    # Game Type Dropdown
    __main__.gGameTypeDrop = ctk.CTkOptionMenu(
        __main__.gApp,
        values=["Steam", "Other"],
        command=__main__.set_game_type_selection,
        corner_radius=0
    )
    
    # Set current game type from config
    __main__.gGameTypeDrop.set(__main__.get_config_value("gametype", default="Steam"))

    # Custom EXE Checkbox
    __main__.gCustom_exe = ctk.IntVar(value=int(__main__.get_config_value("enableopenspy", default="0")))
    __main__.gCustom_exe_button = ctk.CTkCheckBox(
        __main__.gApp,
        text="Enable OpenSpy LAA exe  ",
        variable=__main__.gCustom_exe,
        corner_radius=0,
        command=__main__.custom_exe_manager
    )

     # Enable disable editor

    __main__.gEditor = ctk.IntVar(value=int(__main__.map_editor("read")))
    __main__.gEditor_button = ctk.CTkCheckBox(
        __main__.gApp,
        text="Enable Map Editor  ",
        variable=__main__.gEditor,
        corner_radius=0,
        command=lambda: __main__.map_editor("toggle")
    )
    
    __main__.gInterface_canvas.create_window(25, 690, window=__main__.gStart_button, anchor="w")
    __main__.gInterface_canvas.create_window(25, 180, window=__main__.gUpdate_maps_button, anchor="w")
    __main__.gInterface_canvas.create_window(25, 220, window=__main__.gGameTypeDrop, anchor="w")
    __main__.gInterface_canvas.create_window(25, 260, window=__main__.gCustom_exe_button, anchor="w")
    __main__.gInterface_canvas.create_window(25, 300, window=__main__.gCustom_levels_button, anchor="w")

    __main__.gInterface_canvas.create_window(25, 340, window=__main__.gEditor_button, anchor="w")

    __main__.gInterface_canvas.create_window(25, 380, window=__main__.gGamepath_button, anchor="w")
    __main__.gInterface_canvas.create_window(25, 420, window=__main__.gGameLocation_label, anchor="w")
    __main__.gInterface_canvas.create_window(25, 460, window=__main__.gRemoveSymlink, anchor="w")
    __main__.gInterface_canvas.create_window(25, 650, window=__main__.gLog_button, anchor="w")
    __main__.gInterface_canvas.create_window(25, 690, window=__main__.gStart_button, anchor="w")

    
    __main__.gRemoveSymlink.configure(state="disabled")
    if __main__.gGamePath == "":
        __main__.error_logs(f"[interface] Game path not set", "warning")
        __main__.gCustom_levels_button.configure(state="disabled")
        __main__.gStart_button.configure(state="disabled")
        __main__.gCustom_exe_button.configure(state="disabled")
        __main__.gGameTypeDrop.configure(state="disabled")
    else:
        __main__.gGameLocation_label.configure(text=str(__main__.string_utils(__main__.gGamePath, max_length=30, placeholder="...")))
        __main__.ToolTip(__main__.gGameLocation_label, str(__main__.gGamePath))
        __main__.error_logs(f"[interface] Game Path " + str(__main__.gGamePath), "info")
        __main__.gCustom_levels_button.configure(state="normal")
        __main__.gStart_button.configure(state="normal")
        __main__.gCustom_exe_button.configure(state="normal")
        __main__.gGameTypeDrop.configure(state="normal")

    # Load Maps
    __main__.map_manager()
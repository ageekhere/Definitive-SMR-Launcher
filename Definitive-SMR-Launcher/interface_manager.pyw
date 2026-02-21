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
            __main__.error_logs(f"[unload_map] Removing symlink: {path}", "info")
            path.unlink()
            __main__.gRemoveSymlink.configure(state="disabled")

def interface_manager(os,ctk):
    __main__.error_logs("[interface] Setting up interface", "info")
    __main__.gLog_button = __main__.ctk.CTkButton(__main__.gApp, text=__main__.get_text("gLog_button"), corner_radius=0, command=__main__.debug_window, width=40) # Logs Button
    __main__.gStart_button = __main__.ctk.CTkButton(__main__.gApp, text=__main__.get_text("gStart_button"), command=__main__.game_launcher, corner_radius=0) # Start Game Button
    __main__.gGamePath_button = __main__.ctk.CTkButton(__main__.gApp, text=__main__.get_text("gGamepath_button"), corner_radius=0, command=__main__.gamepath_manager) # Set Game Path Button
    __main__.gUpdate_maps_button = __main__.ctk.CTkButton(__main__.gApp, text=__main__.get_text("gUpdate_maps_button"),corner_radius=0,fg_color="green",width=250, command=__main__.map_updater) # Update Maps Button # Lang key: gUpdate_maps_button
    __main__.gGameLocation_label = __main__.ctk.CTkLabel(__main__.gApp, text=__main__.get_text("gGameLocation_label")) # Game Path Label
    __main__.gRemoveSymlink = __main__.ctk.CTkButton(__main__.gApp, text=__main__.get_text("gRemoveSymlink"), corner_radius=0, command=unload_map)
    __main__.downnload_audio_lang = __main__.ctk.CTkButton(__main__.gApp, text="⭳", corner_radius=0,width=30, command=__main__.download_voice) 
    
    unload_map()

    # Custom Difficulty CTkCheckBox
    __main__.gCustom_difficulty = __main__.ctk.IntVar(value=int(__main__.get_config_value("customdifficulty", default="0")))
    __main__.gCustom_levels_button = __main__.ctk.CTkCheckBox(
        __main__.gApp,
        text=__main__.get_text("gCustom_levels_button"),
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
    __main__.gGameTypeDrop = __main__.ctk.CTkOptionMenu(
        __main__.gApp,
        values=["Steam", "Other"],
        command=__main__.set_game_type_selection,
        corner_radius=0
    )
    
    # Set current game type from config
    __main__.gGameTypeDrop.set(__main__.get_config_value("gametype", default="Steam"))

    # Custom EXE Checkbox
    __main__.gCustom_exe = __main__.ctk.IntVar(value=int(__main__.get_config_value("enableopenspy", default="0")))
    __main__.gCustom_exe_button = __main__.ctk.CTkCheckBox(
        __main__.gApp,
        text=__main__.get_text("gCustom_exe_button"),
        variable=__main__.gCustom_exe,
        corner_radius=0,
        command=__main__.custom_exe_manager
    )

     # Enable disable editor

    __main__.gEditor = __main__.ctk.IntVar(value=int(__main__.map_editor("read")))
    __main__.gEditor_button = __main__.ctk.CTkCheckBox(
        __main__.gApp,
        text=__main__.get_text("gEditor_button"),
        variable=__main__.gEditor,
        corner_radius=0,
        command=lambda: __main__.map_editor("toggle")
    )

    # language Dropdown
    __main__.glanguageDrop = __main__.ctk.CTkOptionMenu(
        __main__.gApp,
        values=["English", "Mandarin Chinese","Hindi","Spanish","French"],
        command=__main__.set_lang_type_selection,
        corner_radius=0
    )
    
    # Set current game type from config
    __main__.glanguageDrop.set(__main__.get_config_value("option3", default="English"))

    if getattr(__main__.sys, 'frozen', False):
        # Running as compiled EXE
        APP_DIR = __main__.Path(__main__.sys.executable).parent
    else:
        # Running as script
        APP_DIR = __main__.Path(__file__).parent

    VOICES_DIR = APP_DIR / "voices_data" / "voices"
    VOICES_DIR.mkdir(parents=True, exist_ok=True)


    MAX_CHARS = 15
    def truncate(text, max_chars=MAX_CHARS):
        return text if len(text) <= max_chars else text[:max_chars-3] + "..."

    def set_audio_lang_type_selection(choice: str):
        try:
            # Persist the new value in config.ini and update globals
            __main__.glanguageAudioDrop.set(truncate(choice))
            __main__.set_config_value("option4", choice)
            __main__.error_logs(f"[set_audio_lang_type_selection] Audio language: {choice}", "info")
        except Exception as e:
            __main__.error_logs(f"[set_audio_lang_type_selection] Failed to update audio: {e}", "error")

    

    # Get all .onnx filenames
    audio_language = __main__.get_config_value("option4")
    onnx_files = [f.name for f in VOICES_DIR.rglob("*.onnx")]
    if not onnx_files:
        audio_language = "Install Voice"
    else:
        if audio_language.strip() == "":
            audio_language = "Select Voice"
    audio_language = truncate(audio_language)

    # lang audio Dropdown

    __main__.glanguageAudioDrop = __main__.ctk.CTkOptionMenu(
        __main__.gApp,
        values=onnx_files,
        command=set_audio_lang_type_selection,
        corner_radius=0
    )
    __main__.glanguageAudioDrop.set(audio_language)

    # --- Function to run when dropdown opens ---
    def on_dropdown_pressed():
        __main__.error_logs("[Dropdown Opened] User clicked audio language dropdown", "info")

    # --- Override the internal _open_dropdown_menu method ---
    original_open = __main__.glanguageAudioDrop._open_dropdown_menu

    def new_open_dropdown_menu():
        audio_language = __main__.get_config_value("option4")
        onnx_files = [f.name for f in VOICES_DIR.rglob("*.onnx")]
        if not onnx_files:
            audio_language = "No Reading Voice"
        else:
            if audio_language.strip() == "":
                audio_language = "Select Voice"
        audio_language = truncate(audio_language)
        __main__.glanguageAudioDrop.configure(values=onnx_files)

        on_dropdown_pressed()  # fires immediately on click
        original_open()        # then open the menu normally

    __main__.glanguageAudioDrop._open_dropdown_menu = new_open_dropdown_menu

    # Set current game type from config
    #__main__.set_audio_lang_type_selection.set(audio_language)

    x_margin = 0.005  # 1% of canvas width
    y_start = 0.29   # 25% down from top
    y_spacing = 0.05 # 5% of canvas height between widgets

    canvas_width = __main__.gInterface_canvas.winfo_width()
    canvas_height = __main__.gInterface_canvas.winfo_height()

    # Compute absolute positions
    x_pos = int(canvas_width * x_margin)

    # Create canvas windows dynamically
    __main__.gUpdate_maps_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * y_start), window=__main__.gUpdate_maps_button, anchor="w")
    __main__.gGameTypeDrop_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing)), window=__main__.gGameTypeDrop, anchor="w")
    __main__.gCustom_exe_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*2)), window=__main__.gCustom_exe_button, anchor="w")
    __main__.gCustom_levels_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*3)), window=__main__.gCustom_levels_button, anchor="w")
    __main__.gEditor_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*4)), window=__main__.gEditor_button, anchor="w")
    __main__.gGamePath_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*5)), window=__main__.gGamePath_button, anchor="w")
    __main__.gGameLocation_label_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*6)), window=__main__.gGameLocation_label, anchor="w")
    __main__.gRemoveSymlink_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*7)), window=__main__.gRemoveSymlink, anchor="w")
    __main__.glanguageDrop_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*8)), window=__main__.glanguageDrop, anchor="w")
    __main__.glanguageAudioDrop_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*9)), window=__main__.glanguageAudioDrop, anchor="w")
    __main__.downnload_audio_lang_id = __main__.gInterface_canvas.create_window(int(canvas_width * 0.133), int(canvas_height * (y_start + y_spacing*9)), window=__main__.downnload_audio_lang, anchor="w")
    __main__.gLog_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*12)), window=__main__.gLog_button, anchor="w")
    __main__.gStart_button_id = __main__.gInterface_canvas.create_window(x_pos, int(canvas_height * (y_start + y_spacing*13)), window=__main__.gStart_button, anchor="w")

    __main__.gRemoveSymlink.configure(state="disabled")
    if __main__.gGamePath == "":
        __main__.error_logs("[interface] Game path not set", "warning")
        __main__.gCustom_levels_button.configure(state="disabled")
        __main__.gStart_button.configure(state="disabled")
        __main__.gCustom_exe_button.configure(state="disabled")
        __main__.gGameTypeDrop.configure(state="disabled")
    else:
        __main__.gGameLocation_label.configure(text=str(__main__.string_utils(__main__.gGamePath, max_length=30, placeholder="...")))
        __main__.ToolTip(__main__.gGameLocation_label, str(__main__.gGamePath))
        __main__.error_logs("[interface] Game Path " + str(__main__.gGamePath), "info")
        __main__.gCustom_levels_button.configure(state="normal")
        __main__.gStart_button.configure(state="normal")
        __main__.gCustom_exe_button.configure(state="normal")
        __main__.gGameTypeDrop.configure(state="normal")

    __main__.ToolTip(__main__.gUpdate_maps_button, __main__.get_text("gUpdate_maps_button"))
    __main__.ToolTip(__main__.gGameTypeDrop, __main__.get_text("gGameTypeDrop"))
    __main__.ToolTip(__main__.gCustom_exe_button, __main__.get_text("Custom_exe_button"))
    __main__.ToolTip(__main__.gCustom_levels_button, __main__.get_text("Custom_levels_button"))
    __main__.ToolTip(__main__.gEditor_button, __main__.get_text("Editor_button"))
    __main__.ToolTip(__main__.gGamePath_button, __main__.get_text("gGamepath_button"))
    __main__.ToolTip(__main__.gRemoveSymlink, __main__.get_text("unload_map"))
    __main__.ToolTip(__main__.glanguageDrop, __main__.get_text("languageDrop"))
    __main__.ToolTip(__main__.glanguageAudioDrop, __main__.get_text("languageAudioDrop"))
    __main__.ToolTip(__main__.downnload_audio_lang, __main__.get_text("downnload_audio_lang"))
    __main__.ToolTip(__main__.gStart_button, __main__.get_text("Start_button_tip"))

    # Load Maps
    __main__.map_manager()
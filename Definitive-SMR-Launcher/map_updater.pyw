"""
map_updater.py

Displays a popup window to allow users to select maps to download or install.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports

def map_updater():
    """
    Popup for map updates. Shows checkboxes for:
      - Maps missing online (need to download)
      - Maps downloaded but not extracted (local)
    """
    try:
        # --- Create new popup and store reference ---
        
        __main__.gUpdateWindow = __main__.ctk.CTkToplevel()

        __main__.gUpdateWindow.title(str(len(__main__.gNewDownloadMaps)) + " New Maps Available To Download")

        # Set size
        width, height = 800, 600
        __main__.gUpdateWindow.geometry(f"{width}x{height}")

        # Keep popup always on top
        __main__.gUpdateWindow.attributes("-topmost", True)

        # Center relative to the main window
        master = __main__.gUpdateWindow.master
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2 - width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2 - height // 2)
        __main__.gUpdateWindow.geometry(f"{width}x{height}+{x}+{y}")

        __main__.create_icon(__main__.sys, __main__.gUpdateWindow)

        # Scrollable frame for checkboxes
        scrollable_frame = __main__.ctk.CTkScrollableFrame(__main__.gUpdateWindow)
        scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)

        checkbox_vars = {}

        # --- Add checkboxes for online download maps ---
        for value in __main__.gNewDownloadMaps:
            var = __main__.ctk.IntVar(value=0)
            checkbox = __main__.ctk.CTkCheckBox(
                scrollable_frame,
                text=f"{value[0]} - Download",
                variable=var
            )
            checkbox.pack(anchor="w", pady=5)
            checkbox_vars[value] = var
            __main__.gUpdateCheckBoxes[str(value[0])] = checkbox

        # --- Add checkboxes for local maps not extracted ---
        for value in __main__.gNewLocalMaps:
            var = __main__.ctk.IntVar(value=0)
            checkbox = __main__.ctk.CTkCheckBox(
                scrollable_frame,
                text=f"{value[0]} - Local",
                variable=var
            )
            checkbox.pack(anchor="w", pady=5)
            checkbox_vars[value] = var
            __main__.gUpdateCheckBoxes[str(value[0])] = checkbox

        # --- Function to install selected maps ---
        def install_maps():
            __main__.gDownloadList = [name[0] for name, var in checkbox_vars.items() if var.get() == 1]
            __main__.error_logs(f"[map_updater] install list {__main__.gDownloadList}", "info")
            install_button.configure(state="disabled")
            selectAll.configure(state="disabled")
            __main__.gCancel_button.configure(state="normal")
            __main__.gStopDownload.set()  # kill the thread
            __main__.map_downloader()

        # --- Select/Deselect all toggle ---
        def show_selected():
            if selectAll.cget("text") == "Select All":
                selectAll.configure(text="Deselect All")
                for var in checkbox_vars.values():
                    var.set(1)
            else:
                selectAll.configure(text="Select All")
                for var in checkbox_vars.values():
                    var.set(0)

        def install_cancel():
            __main__.gCancel_button.configure(state="disabled")
            __main__.gStopDownload.set()  # kill the thread
            __main__.error_logs("[install_cancel] Canceled update", "info")
            install_button.configure(state="normal")
            selectAll.configure(state="normal")
            __main__.gCancel_button.configure(state="disabled")

        # Buttons
        selectAll = __main__.ctk.CTkButton(__main__.gUpdateWindow, text="Select All", command=show_selected)
        selectAll.pack(pady=10, anchor="w")

        install_button = __main__.ctk.CTkButton(__main__.gUpdateWindow, text="Install Maps", command=install_maps)
        install_button.pack(pady=10, anchor="w")

        __main__.gCancel_button = __main__.ctk.CTkButton(__main__.gUpdateWindow, text="Cancel", command=install_cancel)
        __main__.gCancel_button.pack(pady=10, anchor="w")
        __main__.gCancel_button.configure(state="disabled")

        __main__.gStopDownload.set()  # kill the thread


    except Exception as e:
        __main__.error_logs(f"[map_updater] Failed to show map updates popup: {e}", "error")
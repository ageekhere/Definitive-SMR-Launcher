"""
map_updater.py

Displays a popup window to allow users to select maps to download or install.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports
import customtkinter as ctk
import time

def map_updater():
    """
    Popup for map updates. Shows checkboxes for:
      - Maps missing online (need to download)
      - Maps downloaded but not extracted (local)
    """
    try:
        # --- Create new popup and store reference ---
        popup = ctk.CTkToplevel()
        popup.title("Updates")

        # Set size
        width, height = 800, 600
        popup.geometry(f"{width}x{height}")

        # Keep popup always on top
        popup.attributes("-topmost", True)

        # Center relative to the main window
        master = popup.master
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2 - width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2 - height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        # Scrollable frame for checkboxes
        scrollable_frame = ctk.CTkScrollableFrame(popup)
        scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)

        checkbox_vars = {}

        # --- Add checkboxes for online download maps ---
        for value in __main__.gNewDownloadMaps:
            var = ctk.IntVar(value=0)
            checkbox = ctk.CTkCheckBox(
                scrollable_frame,
                text=f"{value[0]} - Download",
                variable=var
            )
            checkbox.pack(anchor="w", pady=5)
            checkbox_vars[value] = var
            __main__.gUpdateCheckBoxes[str(value[0])] = checkbox

        # --- Add checkboxes for local maps not extracted ---
        for value in __main__.gNewLocalMaps:
            var = ctk.IntVar(value=0)
            checkbox = ctk.CTkCheckBox(
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
        selectAll = ctk.CTkButton(popup, text="Select All", command=show_selected)
        selectAll.pack(pady=10, anchor="w")

        install_button = ctk.CTkButton(popup, text="Install Maps", command=install_maps)
        install_button.pack(pady=10, anchor="w")

        __main__.gCancel_button = ctk.CTkButton(popup, text="Cancel", command=install_cancel)
        __main__.gCancel_button.pack(pady=10, anchor="w")
        __main__.gCancel_button.configure(state="disabled")

        __main__.gStopDownload.set()  # kill the thread


    except Exception as e:
        __main__.error_logs(f"[map_updater] Failed to show map updates popup: {e}", "error")
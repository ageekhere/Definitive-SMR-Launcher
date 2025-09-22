"""
map_manager.py

Handles loading and displaying map thumbnails in the launcher interface.
Uses globals and libraries imported in main.py.
"""

import __main__
import pathlib
import time
def map_manager():
    __main__.error_logs("[map_manager] Add maps to interface", "info")

    maps_directory = "maps"
    grid_width = 4
    thumb_size = (233, 233)
    row = col = 0
    thumbnails = []

    for map_folder in __main__.os.listdir(maps_directory):
        folder_path = __main__.os.path.join(maps_directory, map_folder)
        if not __main__.os.path.isdir(folder_path):
            continue

        image_path = __main__.os.path.join(folder_path, "mapIcon.jpg")

        if __main__.os.path.exists(image_path):
            try:
                img = __main__.Image.open(image_path)
                img_ctk = __main__.ctk.CTkImage(light_image=img, dark_image=img, size=thumb_size)
                thumbnails.append(img_ctk)

                # Button click function
                def map_click(m, button):
                    __main__.gSelected_button = getattr(__main__, "gSelected_button", None)

                    if __main__.gSelected_button and __main__.gSelected_button != button:
                        __main__.gSelected_button.configure(fg_color="transparent")
                        __main__.gSelected_button.configure(border_width=0)

                    if button:
                        __main__.gSelected_button = button
                        button.configure(fg_color="#444444")
                        button.configure(border_width=2, border_color="cyan")

                    __main__.gRemoveSymlink.configure(state="normal")
                    for path in __main__.gGameDocs.rglob("*"):
                        if path.is_symlink():
                            __main__.error_logs(f"Removing symlink: {path}", "info")
                            path.unlink()

                    source_path = __main__.os.path.join(__main__.gUsermap_path, m)
                    target_path = __main__.os.path.join(__main__.os.getcwd(), "maps", m, "UserMaps")
                    __main__.create_symlink(source_path, target_path, True)

                    source_path = __main__.os.path.join(__main__.gCustomAssets_path, m)
                    target_path = __main__.os.path.join(__main__.os.getcwd(), "maps", m, "CustomAssets")
                    __main__.create_symlink(source_path, target_path, True)

                    maps_directory = pathlib.Path(__main__.os.path.join(__main__.os.getcwd(), "maps", m))

                    count = 0
                    __main__.error_logs(f"[map_manager] Touching all files for map " + str(m), "info")
                    for files in maps_directory.rglob("*"):  # recursive search
                        try:
                            # Update the file timestamp (acts like `touch`)
                            __main__.os.utime(files, None)
                            count += 1
                        except Exception as e:
                            __main__.error_logs(f"[map_manager] Error touching {files}: {e}", "error")

                btn = __main__.ctk.CTkButton(
                    __main__.gScrollable_frame,
                    image=img_ctk,
                    text="",
                    width=thumb_size[0],
                    height=thumb_size[1],
                    fg_color="transparent"
                )
                btn.configure(command=lambda m=map_folder, b=btn: map_click(m, b))
                btn.grid(row=row, column=col, padx=5, pady=20,sticky="n")

                info_btn = __main__.ctk.CTkButton(
                    __main__.gScrollable_frame,
                    width=thumb_size[0],
                    corner_radius=0,
                    text=f"ⓘ {map_folder}",
                    command=__main__.partial(__main__.map_info_manager, map_folder)
                )
                info_btn.grid(row=row, column=col, padx=5, pady=0,sticky="n")

                col += 1
                if col >= grid_width:
                    col = 0
                    row += 2

            except Exception as e:
                __main__.error_logs(f"Failed to load {image_path}: {e}", "error")

    # Check for missing maps
    missing_maps = __main__.map_checker()

    if missing_maps == ([], []):
        __main__.gUpdate_maps_button.configure(state="disabled")
"""
Optimized map_manager.py - Improved popup: stays open until everything is loaded
- Shows image loading progress
- Then shows "Building interface..." during widget creation
- Closes only after final chunk is placed
- Popup appears immediately
"""

import __main__
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import pickle
import os
import threading
from PIL import Image as PILImage

# Thread pools
rating_executor = ThreadPoolExecutor(max_workers=5)
image_executor = ThreadPoolExecutor(max_workers=3)

__main__.thumb_cache_folder = "maps/.thumb_cache"
os.makedirs(__main__.thumb_cache_folder, exist_ok=True)

last_call_time = 0
throttle_interval = 2000  # milliseconds

CACHE_VERSION = 2

# -------------------- Rating Functions --------------------
def load_rating_async(map_name, info_btn):
    try:
        if map_name in __main__.gRatingCache:
            stars = __main__.gRatingCache[map_name]
        else:
            url = __main__.get_map_data(map_name, __main__.gMap_rating_matrix, "url")
            if not url:
                __main__.gScrollable_frame.after(0, lambda: update_rating_ui(info_btn, ""))
                return
            rating_list = __main__.get_map_rating(str(url))
            text_value = float(rating_list[6].strip("()").split("/")[0])
            if text_value >= 5.0:
                stars = "⭐⭐⭐⭐⭐"
            elif text_value >= 4.0:
                stars = "⭐⭐⭐⭐"
            elif text_value >= 3.0:
                stars = "⭐⭐⭐"
            elif text_value >= 2.0:
                stars = "⭐⭐"
            elif text_value >= 1.0:
                stars = "⭐"
            else:
                stars = "🛑"
            __main__.gRatingCache[map_name] = stars
        __main__.gScrollable_frame.after(0, lambda: update_rating_ui(info_btn, stars))
    except Exception as e:
        __main__.error_logs(f"[rating_async] {map_name}: {e}", "error")


def update_rating_ui(info_btn, stars):
    try:
        current_text = info_btn.cget("text").replace("⏳ Loading...", "").strip()
        if stars:
            info_btn.configure(text=current_text + " " + stars)
        else:
            info_btn.configure(text=current_text)
    except Exception as e:
        __main__.error_logs(f"[update_rating_ui]: {e}", "error")


# -------------------- Image Functions --------------------
def get_thumb_cache_path(map_folder):
    h = hashlib.md5(map_folder.encode("utf-8")).hexdigest()
    return os.path.join(__main__.thumb_cache_folder, f"{h}.pkl")


def load_image(map_folder):
    try:
        cache_file = get_thumb_cache_path(map_folder)
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, tuple) and len(data) == 2 and data[0] == CACHE_VERSION:
                    pil_img = data[1]
                    if isinstance(pil_img, PILImage.Image):
                        return pil_img, map_folder

        image_path = os.path.join("maps", map_folder, "mapIcon.jpg")
        if not os.path.exists(image_path):
            return None, map_folder

        pil_img = PILImage.open(image_path).convert("RGB")
        pil_img.thumbnail((233, 233), PILImage.LANCZOS)

        with open(cache_file, "wb") as f:
            pickle.dump((CACHE_VERSION, pil_img), f)

        return pil_img, map_folder
    except Exception as e:
        __main__.error_logs(f"[load_image] Failed {map_folder}: {e}", "error")
        return None, map_folder


# -------------------- Map Manager --------------------
def map_manager():
    global last_call_time
    now = int(__main__.time.time() * 1000)
    if now - last_call_time < throttle_interval:
        return
    last_call_time = now
    threading.Thread(target=map_manager_thread, name="map_manager", daemon=True).start()


def map_manager_thread():
    __main__.gMapMangerTheadRunning = True
    __main__.error_logs("[map_manager_thread] Starting map load", "info")

    if __main__.gDownloadingMapStatus:
        __main__.error_logs("[map_manager_thread] Skipping due to download", "info")
        __main__.gMapMangerTheadRunning = False
        return

    # Cleanup symlinks
    for path in __main__.gGameDocs.rglob("*"):
        if path.is_symlink():
            path.unlink()
    __main__.gRemoveSymlink.configure(state="disabled")

    map_folders = [f for f in os.listdir("maps") if os.path.isdir(os.path.join("maps", f))]
    total_maps = len(map_folders)
    if total_maps == 0:
        __main__.gMapMangerTheadRunning = False
        return

    # Create popup immediately
    popup = None
    popup_label = None

    def create_popup_now():
        nonlocal popup, popup_label
        popup = __main__.ctk.CTkToplevel(__main__.gApp)
        popup.overrideredirect(True)
        popup_width, popup_height = 300, 100
        x = __main__.gApp.winfo_rootx() + (__main__.gApp.winfo_width() - popup_width) // 2
        y = __main__.gApp.winfo_rooty() + (__main__.gApp.winfo_height() - popup_height) // 2
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup_label = __main__.ctk.CTkLabel(popup, text="Loading images: 0%", font=("Helvetica", 14))
        popup_label.pack(expand=True, fill="both")
        popup.grab_set()
        popup.attributes('-topmost', True)
        popup.update()
        __main__.gApp.update_idletasks()

    __main__.gScrollable_frame.after(0, create_popup_now)
    # Force popup to appear quickly
    for _ in range(4):
        __main__.gApp.update()
        __main__.gApp.update_idletasks()

    # Start parallel image loading
    futures = [image_executor.submit(load_image, folder) for folder in map_folders]
    results = []

    def set_image_progress(p, t):
        if popup_label is None:
            return
        try:
            percent = int((p / t) * 100)
            popup_label.configure(text=f"Loading images: {percent}%")
            popup.update_idletasks()
        except:
            pass

    processed_count = 0
    for future in as_completed(futures):
        try:
            res = future.result()
            results.append(res)
        except Exception as e:
            __main__.error_logs(f"Image future error: {e}", "error")
        finally:
            processed_count += 1
            __main__.gScrollable_frame.after(0, lambda pp=processed_count, tt=total_maps: set_image_progress(pp, tt))

    # Switch to building phase
    __main__.gScrollable_frame.after(0, lambda: set_building_phase(popup_label, popup))

    # Start widget creation
    __main__.gScrollable_frame.after(0, lambda: create_map_widgets(results, popup, popup_label, total_maps))


def set_building_phase(popup_label, popup):
    if popup_label is None:
        return
    try:
        popup_label.configure(text="Building interface...")
        popup.update_idletasks()
    except:
        pass


def create_map_widgets(results, popup, popup_label, total_maps):
    CHUNK_SIZE = 25
    image_size = 233
    spacing = 10
    effective_width = image_size + spacing
    grid_width = max(1, __main__.gScrollable_frame.winfo_width() // effective_width)

    if not hasattr(__main__, "gRatingCache"):
        __main__.gRatingCache = {}

    row = col = 0
    processed = 0

    def add_chunk(start_idx):
        nonlocal row, col, processed

        end_idx = min(start_idx + CHUNK_SIZE, len(results))
        for i in range(start_idx, end_idx):
            pil_img, map_folder = results[i]
            if pil_img is None:
                processed += 1
                continue

            try:
                ctk_img = __main__.ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(233, 233))

                btn = __main__.ctk.CTkButton(
                    __main__.gScrollable_frame,
                    image=ctk_img,
                    text="",
                    width=233,
                    height=233,
                    fg_color="transparent",
                )
                btn.grid(row=row, column=col, padx=0, pady=7, sticky="n")

                btn.configure(command=lambda button=btn, m=map_folder: map_click(m=m, button=button))

                def map_click(m, button):
                    folder = __main__.Path(__main__.os.getcwd()) / "maps" / m
                    for file in folder.rglob("*"):
                        if file.is_file():
                            file.touch()

                    if hasattr(__main__, "gSelected_button") and __main__.gSelected_button != button and __main__.gSelected_button != None:
                        __main__.gSelected_button.configure(fg_color="transparent", border_width=0)
                    __main__.gSelected_button = button
                    button.configure(fg_color="#444444", border_width=2, border_color="cyan")
                    __main__.gRemoveSymlink.configure(state="normal")

                    for path in __main__.gGameDocs.rglob("*"):
                        if path.is_symlink():
                            path.unlink()

                    source = os.path.join(__main__.gUsermap_path, m)
                    target = os.path.join(os.getcwd(), "maps", m, "UserMaps")
                    __main__.create_symlink(source, target, True)

                    source = os.path.join(__main__.gCustomAssets_path, m)
                    target = os.path.join(os.getcwd(), "maps", m, "CustomAssets")
                    __main__.create_symlink(source, target, True)

                # Info button
                def ellipsize(text, max_chars=25):
                    return text if len(text) <= max_chars else text[:max_chars-3] + "..."

                display_text = ellipsize(map_folder)
                map_name = map_folder
                info_color = "#1f6aa5"
                text_color = "#ffffff"

                name_data = __main__.get_map_data(map_name, __main__.gMap_rating_matrix, "name")
                if name_data:
                    display_text = ellipsize(name_data, 27)

                map_name_data = __main__.get_map_data(map_folder, __main__.gMap_rating_matrix, "Map Name")
                if map_name_data:
                    map_name = map_name_data

                if __main__.get_map_data(map_folder, __main__.gMap_rating_matrix, "is_stable") == "n":
                    text_color = "black"
                    info_color = "#d48806"
                    display_text = "⚠ " + display_text

                multi = __main__.get_map_data(map_folder, __main__.gMap_rating_matrix, "multiplayer")
                if multi == "n":
                    display_text += "\n 👤 "
                elif multi == "y":
                    display_text += "\n 👤👤 "

                has_rating = __main__.get_map_data(map_name, __main__.gMap_rating_matrix, "url") is not None
                if has_rating:
                    display_text += "\n⏳ Loading..."

                info_btn = __main__.ctk.CTkButton(
                    __main__.gScrollable_frame,
                    width=233,
                    height=40,
                    corner_radius=0,
                    fg_color=info_color,
                    bg_color=info_color,
                    text=f"ⓘ {display_text}",
                    text_color=text_color,
                    font=__main__.ctk.CTkFont(size=16),
                    border_width=0,
                    command=__main__.partial(__main__.map_info_manager, map_folder)
                )
                info_btn.grid(row=row, column=col, padx=0, pady=11, sticky="n")

                if has_rating:
                    rating_executor.submit(load_rating_async, map_name, info_btn)

                col += 1
                if col >= grid_width:
                    col = 0
                    row += 2

                processed += 1
            except Exception as e:
                __main__.error_logs(f"Widget creation error at {i}: {e}", "error")
                processed += 1

        if end_idx < len(results):
            __main__.gScrollable_frame.after(20, lambda: add_chunk(end_idx))
        else:
            # All widgets placed → show done and close after short delay
            __main__.gScrollable_frame.after(0, lambda: set_done_phase(popup_label, popup))
            __main__.gScrollable_frame.after(400, lambda: finish_and_close(popup))

    def set_done_phase(popup_label, popup):
        if popup_label is None:
            return
        try:
            popup_label.configure(text="Done!")
            popup.update_idletasks()
        except:
            pass

    def finish_and_close(popup):
        try:
            missing_maps = __main__.map_checker()
            if missing_maps == ([], []):
                __main__.gUpdate_maps_button.configure(state="disabled")
        except:
            pass

        if popup is not None:
            try:
                popup.destroy()
            except:
                pass

        __main__.gMapMangerTheadRunning = False
        __main__.gScrollable_frame.update_idletasks()

    add_chunk(0)
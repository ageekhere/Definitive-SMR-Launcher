import customtkinter as ctk
import requests
from pathlib import Path
import threading
import hashlib
import json
import os
import time
from datetime import datetime
import __main__
from bs4 import BeautifulSoup
from tkinter import messagebox

# ----------------------
# CONFIG
# ----------------------
VOICE_SAVE_DIR = Path("voices_data/voices")
VOICE_SAVE_DIR.mkdir(parents=True, exist_ok=True)
VOICES_JSON_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/voices.json"
HF_TOKEN = None
CACHE_FILE = "piper_voice_dates_cache.json"
CACHE_TTL_SECONDS = 60 * 60 * 24 * 7
UPDATE_DATE_CACHE = {}
RETRY_DELAY_ON_429 = 10
heading_text = None
sub_heading_text = None
# ----------------------
# CACHE LOAD/SAVE
# ----------------------
def load_date_cache():
    global UPDATE_DATE_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                UPDATE_DATE_CACHE = {}
                for k, v in raw.items():
                    if isinstance(v, str):
                        UPDATE_DATE_CACHE[k] = [v, time.time()]
                    elif isinstance(v, list) and len(v) == 2:
                        UPDATE_DATE_CACHE[k] = v
            __main__.error_logs(f"[load_date_cache]Loaded {len(UPDATE_DATE_CACHE)} cached date entries", "info")
        except Exception as e:
            __main__.error_logs(f"[load_date_cache]Cache load failed: {e}", "error")
            UPDATE_DATE_CACHE = {}

def save_date_cache():
    try:
        clean_cache = {}
        for k, v in UPDATE_DATE_CACHE.items():
            if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and v[1] > 1600000000:
                clean_cache[k] = v
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_cache, f, ensure_ascii=False, indent=2)

        __main__.error_logs(f"[save_date_cache] Date cache saved", "info")
    except Exception as e:
        __main__.error_logs(f"[save_date_cache]Cache save failed: {e}", "error")

# ----------------------
# FETCH VOICE LIST + MD5 + STATUS
# ----------------------
def fetch_piper_voice_list():
    try:
        resp = requests.get(VOICES_JSON_URL, timeout=15)
        resp.raise_for_status()
        voices_json = resp.json()
    except Exception as e:
        __main__.error_logs(f"[fetch_piper_voice_list]Error fetching voices.json: {e}", "error")
        return []
    voices_list = []
    for voice_id, voice_info in voices_json.items():
        voices_list.append({"id": voice_id, "files": voice_info.get("files", {})})
    return voices_list

def calculate_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_remote_md5(voice):
    for file_path, meta in voice["files"].items():
        if file_path.endswith(".onnx"):
            return meta.get("md5_digest")
    return None

def get_local_onnx_path(voice_id):
    local_dir = VOICE_SAVE_DIR / voice_id
    if not local_dir.exists():
        return None
    for f in local_dir.glob("*.onnx"):
        return f
    return None

def get_voice_status(voice):
    local_path = get_local_onnx_path(voice["id"])
    remote_md5 = get_remote_md5(voice)
    if not local_path:
        return "not_installed"
    try:
        local_md5 = calculate_md5(local_path)
    except Exception:
        return "not_installed"
    return "up_to_date" if local_md5 == remote_md5 else "update_available"

# ----------------------
# CACHE VALIDITY + FETCH DATE
# ----------------------
def is_usable_cached_value(cached_entry):
    if not isinstance(cached_entry, list) or len(cached_entry) != 2:
        return False, None
    display, cache_time = cached_entry
    now = time.time()
    lower_display = display.lower()
    always_retry_phrases = ["fetch failed", "fail", "error", "http ", "429", "limited", "rate limited", "no .onnx", "unknown"]
    if any(phrase in lower_display for phrase in always_retry_phrases):
        return False, None
    if now - cache_time > CACHE_TTL_SECONDS:
        return False, None
    return True, display

def fetch_date_background(voice, date_label, popup_ref, popup_alive):
    voice_id = voice["id"]
    cached = UPDATE_DATE_CACHE.get(voice_id)
    usable, cached_text = is_usable_cached_value(cached)
    if usable:
        popup_ref.after(0, lambda lbl=date_label, txt=cached_text:
            lbl.configure(text=txt) if popup_alive[0] else None)
        return

    onnx_path = next((fp for fp in voice["files"] if fp.endswith(".onnx")), None)
    if not onnx_path:
        popup_ref.after(0, lambda lbl=date_label, txt="No .onnx":
            lbl.configure(text=txt) if popup_alive[0] else None)
        return

    popup_ref.after(0, lambda lbl=date_label, txt="Fetching...":
        lbl.configure(text=txt) if popup_alive[0] else None)

    success = False
    display = "Fetch failed"
    for attempt in range(6):
        try:
            blob_url = f"https://huggingface.co/rhasspy/piper-voices/blob/main/{onnx_path}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            if HF_TOKEN:
                headers["Authorization"] = f"Bearer {HF_TOKEN}"
            r = requests.get(blob_url, headers=headers, timeout=15)
            if r.status_code == 429:
                wait_time = RETRY_DELAY_ON_429 * (attempt + 1)
                popup_ref.after(0, lambda lbl=date_label, wt=wait_time:
                    lbl.configure(text=f"Rate limited – retry in {wt}s") if popup_alive[0] else None)
                time.sleep(wait_time)
                continue
            if r.status_code != 200:
                display = f"HTTP {r.status_code}"
                break
            soup = BeautifulSoup(r.text, "html.parser")
            time_elem = soup.find("time", class_="timeago") or soup.find("time") or \
                        soup.find(string=lambda t: t and "ago" in t.lower())
            display = (time_elem.get_text(strip=True) if time_elem else "Updated recently") or "Updated recently"
            success = True
            break
        except Exception as e:
            __main__.error_logs(f"[fetch_date_background] Fetch failed {voice_id} (attempt {attempt+1}): {e}", "error")
            time.sleep(min(15, 2 ** attempt))

    if success and not any(w in display.lower() for w in ["error", "fail", "http", "limited", "429", "fetch failed"]):
        UPDATE_DATE_CACHE[voice_id] = [display, time.time()]

    popup_ref.after(0, lambda lbl=date_label, txt=display:
        lbl.configure(text=txt) if popup_alive[0] else None)

# ----------------------
# DOWNLOAD HELPERS (minimal addition)
# ----------------------
def get_onnx_and_json_paths(voice):
    onnx_p = None
    json_p = None
    for fp in voice["files"]:
        if fp.endswith(".onnx"):
            onnx_p = fp
        elif fp.endswith(".onnx.json"):
            json_p = fp
    return onnx_p, json_p

def build_file_url(rel_path):
    base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
    return f"{base_url}/{rel_path}?download=true"

# ----------------------
# DOWNLOAD + PROTECT CLOSE (modified minimally)
# ----------------------
def download_voice_files(voice, status_label, download_in_progress):
    download_in_progress[0] = True
    try:
        status_label.configure(text=f"Downloading {voice['id']}...")
        local_dir = VOICE_SAVE_DIR / voice["id"]
        local_dir.mkdir(parents=True, exist_ok=True)

        onnx_rel, json_rel = get_onnx_and_json_paths(voice)
        
        if not onnx_rel:
            raise Exception("No .onnx file found")

        base = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

        # Download model
        r = requests.get(build_file_url(onnx_rel), stream=True, timeout=90)
        r.raise_for_status()
        onnx_path = local_dir / Path(onnx_rel).name
        with open(onnx_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=32768):
                f.write(chunk)

        # Download config if it exists
        if json_rel:
            status_label.configure(text=f"Downloading config for {voice['id']}...")
            r = requests.get(build_file_url(json_rel), stream=True, timeout=30)
            r.raise_for_status()
            json_path = local_dir / Path(json_rel).name
            with open(json_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        status_label.configure(text=f"Installed / Updated {voice['id']} ✔")

    except Exception as e:
        status_label.configure(text=f"Error: {str(e)}")
    finally:
        download_in_progress[0] = False

# ----------------------
# UI
# ----------------------
def download_voice():
    global popup
    global heading_text
    global sub_heading_text
    load_date_cache()
    voices = fetch_piper_voice_list()
    if not voices:
        ctk.messagebox.showerror("Error", "Could not fetch Piper voices list.")
        return

    popup = ctk.CTkToplevel()
    popup.title("Install Piper Voice")
    popup.geometry("1000x720")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    popup_alive = [True]
    download_in_progress = [False]

    try:
        __main__.create_icon(__main__.sys, popup)
    except:
        pass


    heading_text = ctk.CTkLabel(
        popup,
        text=__main__.get_text("loading_voices"),
        font=("Arial", 16, "bold")
        )

    heading_text.pack(pady=(15, 5))

    sub_heading_text = ctk.CTkLabel(
        popup, 
        text="",
        font=("Arial", 11),
        text_color="gray",
        wraplength=900
    )

    sub_heading_text.pack(pady=(0, 10))

    scroll_frame = ctk.CTkScrollableFrame(popup, height=540)
    scroll_frame.pack(fill="both", padx=20, pady=(0, 10), expand=True)

    status_label = ctk.CTkLabel(popup, text="", font=("Arial", 12))
    status_label.pack(pady=(5, 10))

    date_labels = {}

    def refresh_list():
        global heading_text
        global sub_heading_text
        
        heading_text.configure(text=__main__.get_text("voice_heading"))
        sub_heading_text.configure(text=__main__.get_text("voice_sub_heading"))
        if not popup_alive[0]:
            return
        to_remove = [vid for vid, entry in UPDATE_DATE_CACHE.items() if not is_usable_cached_value(entry)[0]]
        for vid in to_remove:
            UPDATE_DATE_CACHE.pop(vid, None)
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        date_labels.clear()
        for voice in voices:
            status = get_voice_status(voice)
            color = "#2ecc71" if status == "up_to_date" else "#f1c40f" if status == "update_available" else "transparent"
            status_text = "Up to date" if status == "up_to_date" else "Update available" if status == "update_available" else "Not installed"
            frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            frame.pack(fill="x", pady=3, padx=4)
            btn = ctk.CTkButton(
                frame,
                text=f"{voice['id']} | {status_text} | ",
                fg_color=color if color != "transparent" else "transparent",
                hover_color=("gray80", "gray25"),
                anchor="w",
                font=("Arial", 13),
                command=lambda v=voice: install_voice(v)
            )
            btn.pack(side="left", fill="x", expand=True)
            date_lbl = ctk.CTkLabel(frame, text="—", font=("Arial", 12), text_color="gray")
            date_lbl.pack(side="right", padx=10)
            date_labels[voice["id"]] = date_lbl
            threading.Thread(
                target=fetch_date_background,
                args=(voice, date_lbl, popup, popup_alive),
                daemon=True
            ).start()

    def install_voice(voice):
        threading.Thread(
            target=download_voice_files,
            args=(voice, status_label, download_in_progress),
            daemon=True
        ).start()
        popup.after(12000, lambda: refresh_list() if popup_alive[0] else None)

    def on_close():
        if download_in_progress[0]:
            messagebox.showwarning(
                __main__.get_text("voice_download_heading"),
                __main__.get_text("voice_download_sub_heading"),
                parent=popup
            )
            return
        popup_alive[0] = False
        save_date_cache()
        popup.destroy()
        #__main__.update_audio_dropdown()
        __main__.update_audio_dropdown()

    popup.protocol("WM_DELETE_WINDOW", on_close)
    ctk.CTkButton(popup, text="Refresh List", width=200, command=refresh_list).pack(pady=(10, 15))
    popup.after(500, refresh_list)

# --- Standard Library Imports ---
import os                      # File system operations
import sys                     # System-specific parameters and functions
import time
import threading
import shutil
import ctypes
from ctypes import windll       # Windows API access (e.g., DPI awareness)
from functools import partial   # Pass arguments into callbacks

from pathlib import Path        # Object-oriented filesystem paths
from threading import Event, Thread, Timer   # Multithreading support
from configparser import ConfigParser

# --- Third-Party Libraries ---
import customtkinter as ctk     # Modern themed Tkinter GUI
import imageio                  # Read/write a wide range of image formats
import py7zr
import pyzipper                 # Advanced ZIP handling (e.g., AES encryption)
import requests                 # HTTP requests (download files, APIs)
import tkinter as tk
from PIL import Image, ImageTk  # Image handling and displaying in Tkinter
from tkinter import filedialog  # File/directory selection dialogs
import win32com.client          # Windows COM automation (shortcuts, Office, etc.)

# --- Local/Project Imports ---
# Config / Settings
from config_manager import get_config_value, make_config, read_write_config, set_config_value
from error_logs import error_logs
from custom_exe_manager import custom_exe_manager
from difficulty_manager import difficulty_manager
from enable_editor import map_editor
from file_operations import file_operations
from folder_watcher import main_watcher

# GUI / Interface
from create_icon import create_icon
from create_splash import create_splash
from debug_window import debug_window
from interface_manager import interface_manager
from tool_tip import ToolTip

# Map-related
from archive_maps import archive_maps
from get_map_data import get_map_data
from load_map_rating import load_map_ratings_matrix
from map_checker import map_checker
from map_downloader import map_downloader
from map_download_extract import map_download_extract
from map_extractor import map_extractor
from map_info_manager import map_info_manager
from map_manager import map_manager
from map_star_rating import get_map_rating
from map_update_worker import map_update_worker
from map_updater import map_updater
from rating_check import rating_check
from set_game_type_selection import set_game_type_selection
from update_maps_timer import update_maps_timer

# Game / Launcher
from game_launcher import game_launcher
from gamepath_manager import gamepath_manager

#Other
from github_update import github_update
from stop_thread import stopThread
from create_symlink import create_symlink
from string_utils import string_utils
from check_openspy import check_openspy
from text_audio import text_audio
from text_audio import stop_button_pressed
from tkinter import messagebox
import json
from download_voice import download_voice
from translate import translate_text
from set_lang_type_selection import set_lang_type_selection
from is_map_manager_running import is_map_manager_running
from check_for_popup_window import check_for_popup_window
from on_popup_close import on_popup_close
from resize_interface import resize_interface
from update_audio_dropdown import update_audio_dropdown
from resource_path import resource_path
from get_text import get_text
"""
class AppState:
    #self.gGamePath = ""
    def __init__(self):
        #self.gOnlineServers = 0
        #self.gPlayersInGame = 0
        #self.gVersion: str = "1.06"

    def update_title(self):
        #global_vars.
        gApp.title(
            f"{get_text("gApp_title")} " 
            f"{self.gVersion} ("
            f"{get_text("OnlineServers")} "
            f"{self.gOnlineServers} | "
            f"{get_text("PlayersInGame")} "
            f"{self.gPlayersInGame})"
            )
"""
if __name__ == '__main__':

    #global_vars = AppState()
    # ------------ ---------- GUI / Widgets ----------------------
    gBackGroundImageUrl: str = r"interface\background.jpg"  # Must be defined FIRST
    gApp: ctk.CTk = ctk.CTk()  # Main app window
    gEditor = None
    gEditor_button = None
    gInstallLogTextbox = None
    gInterface_canvas = None
    gLogWindow = None
    gLogWindowTextbox = ""  # Log textbox updated during runtime
    gLog_button = None
    gScrollable_frame = None
    gSelected_button = None
    gStart_button = None
    gUpdateWindow = None
    gUpdate_maps_button = None
    gGamepath_button = None
    gGameLocation_label = None

    # ---------------------- Paths / Config ----------------------
    #gConfigPath: Path = None
    gConfigUserData: ConfigParser = None
    gConfigUserInfo = None
    gCustomAssets_path = None
    gGameDocs = None
    gUsermap_path = None
    gGamePath = ""

    # ---------------------- Game / App state ----------------------
    gCustom_difficulty = None
    gCustom_exe = None
    gCustom_exe_button = None
    gCustom_levels_button = None
    gMap_editor_option = None
    gDownloadList = None
    gDownloadThread = None
    gRemoveSymlink = None
    gSelected_option = ctk.StringVar(value="Not selected")  # default
    gStopDownload = threading.Event()
    gDownloadingMapStatus = False
    gUpdateCheckBoxes = {}
    gCustomExe = False
    gMap_rating_matrix = None
    gNewDownloadMaps = None
    gNewLocalMaps = None
    gOnlineServers = None
    gPlayersInGame = None
    gSpeech_btn = None
    gEncoding_label = None
    gLanguage = ""
    gGameTypeDrop = None
    glanguageDrop = None
    gLanguage_file = None 
    glanguageAudioDrop = None
    downnload_audio_lang = None
    gSelected_translation = "en"
    gScrollable_frame_width=995
    gVersion = None
    gStart_button_id = None
    gLog_button_id = None
    downnload_audio_lang_id = None
    glanguageAudioDrop_id = None
    glanguageDrop_id = None
    gRemoveSymlink_id = None
    gGameLocation_label_id = None
    gGamePath_button_id = None
    gEditor_button_id = None
    gCustom_levels_button_id = None
    gCustom_exe_button_id = None
    gGameTypeDrop_id = None
    gUpdate_maps_button_id = None
    gResizing = False
    gMapMangerTheadRunning = False


    # ---------------------- GitHub / Version info ----------------------
    gGitHubBranch = "main"
    gGitHubOwner = "ageekhere"
    gGitHubRepo = "Definitive-SMR-Launcher"
    gGitHubVersion: str = "version1.06"
    gVersion: str = "1.06"
    ginternetArchiveIdentifier = "sid-meiers-railroads-custom-maps-collection"

    # ---------------------- Fonts / Geometry ----------------------
    gAppHeight = 720
    gAppWidth = 1280
    gMain_font = ctk.CTkFont(family="arial", size=19, weight="bold")

    # ---------------------- Debug / Logging ----------------------
    gDebug: bool = True
    gLogs: list = []
    # ---------------------- Initialization ----------------------
    # Fix Windows console Unicode issues (prevents UnicodeEncodeError with → etc.)
    """
    if sys.platform.startswith("win"):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')
    """

    error_logs("[Main] Welcome to Definitive-SMR-Launcher", "info")
    error_logs(f"[Main] Python version: {sys.version}")

    ctk.deactivate_automatic_dpi_awareness()

    error_logs("[Main] Disabled DPI awareness", "info")

    ctk.set_appearance_mode("dark")
    error_logs("[Main] set_appearance_mode to Dark", "info")

    ctk.set_default_color_theme("blue")
    error_logs("[Main] set_default_color_theme to blue", "info")

    create_splash() # Splash screen
    
    gApp.minsize(gAppWidth, gAppHeight)

    make_config() # User config

    def get_app_dir():
        """Where the exe lives (writable location)"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent

    APP_DIR = get_app_dir()

    gLanguage = get_config_value("option3")
    if gLanguage == "":
        gLanguage = "English"
        set_config_value("option3", "English")

    if gLanguage == "English":
        path = APP_DIR /"lang"/"English.json"
        with open(path, "r", encoding="utf-8") as f:
            gLanguage_file = json.load(f)

    elif gLanguage == "Mandarin Chinese":
        path = APP_DIR /"lang"/"Mandarin_Chinese.json"
        with open(path, "r", encoding="utf-8") as f:
            gLanguage_file = json.load(f)

    elif gLanguage == "Hindi":
        path = APP_DIR /"lang"/"Hindi.json"
        with open(path, "r", encoding="utf-8") as f:
            gLanguage_file = json.load(f)

    elif gLanguage == "Spanish":
        path = APP_DIR /"lang"/"Spanish.json"
        with open(path, "r", encoding="utf-8") as f:
            gLanguage_file = json.load(f)

    elif gLanguage == "French":
        path = APP_DIR /"lang"/"French.json"
        with open(path, "r", encoding="utf-8") as f:
            gLanguage_file = json.load(f)

    gApp.title(get_text("gApp_title") + " " + str(gVersion)) # Lag key: gApp_title

    # Center window
    mainWindowX = (gApp.winfo_screenwidth() - gAppWidth) // 2
    mainWindowY = (gApp.winfo_screenheight() - gAppHeight) // 6
    gApp.geometry(f"{gAppWidth}x{gAppHeight}+{mainWindowX}+{mainWindowY}")

    gIcon = create_icon(sys, gApp)

    if get_config_value("enableopenspy") == "1":
        gCustomExe = True
        
    original_bg_image = None
    # ---------------------- Background Image ----------------------
    if getattr(sys, 'frozen', False):
        bg_image_path = os.path.join(sys._MEIPASS, "background.jpg")
        error_logs("[Main] Background path " + str(bg_image_path), "info")
    else:
        bg_image_path = gBackGroundImageUrl
        error_logs("[Main] Background path " + str(bg_image_path), "info")

    try:
        bg_image = Image.open(bg_image_path)
        original_bg_image = Image.open(bg_image_path) 
        error_logs("[Main] Loading background Image Successful", "info")
    except FileNotFoundError as e:
        error_logs("[Main] Loading background Image Failed " + str(e), "error")
        sys.exit(1)


    gInterface_canvas = ctk.CTkCanvas(gApp, highlightthickness=0, bg='black')
    gInterface_canvas.pack(fill="both", expand=True)

    bg_image = bg_image.resize((gAppWidth, gAppHeight))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_canvas_id = gInterface_canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # ---------------------- User Paths ----------------------
    shell = win32com.client.Dispatch("WScript.Shell")

    gUsermap_path = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "UserMaps"
    error_logs("[Main]  UserMaps path: " + str(gUsermap_path), "info")

    gCustomAssets_path = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "CustomAssets"
    error_logs("[Main]  CustomAssets path: " + str(gCustomAssets_path), "info")

    gGameDocs = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads"
    error_logs("[Main]  MyDocuments path to Sid Meier's Railroads: " + str(gGameDocs), "info")

    # ---------------------- Scrollable Frame ----------------------
    gScrollable_frame = ctk.CTkScrollableFrame(gInterface_canvas, corner_radius=0, width=995, height=gAppHeight)
    gScrollable_frame.place(x=270)

    # ---------------------- Splash close ----------------------
    try:
        import pyi_splash
        pyi_splash.close()
        error_logs("[close_splash] Splash screen closed", "info")
    except ImportError:
        error_logs("[close_splash] No splash to close", "warning")

    # ---------------------- Directories ----------------------
    maps_dir_path = Path(os.getcwd()) / "maps"
    maps_dir_path.mkdir(parents=True, exist_ok=True)
    download_dir_path = Path(os.getcwd()) / "downloads"
    download_dir_path.mkdir(parents=True, exist_ok=True)
    gMap_rating_matrix = load_map_ratings_matrix(False)
    
    gSelected_translation = get_config_value("option5")
    if gSelected_translation == "" or gSelected_translation == " ":
        gSelected_translation = "en"
        set_config_value("option5", "en")

    def after_gui_loaded():
        map_checker()
        interface_manager(os, ctk)
        github_update()
        main_watcher()
        check_openspy()
        update_maps_timer()
        gApp.protocol("WM_DELETE_WINDOW", on_popup_close)
        gApp.bind("<Configure>",lambda event: resize_interface(event))

    gApp.after(100, after_gui_loaded)

gApp.mainloop()
# --- Standard Library Imports ---
import os                      # File system operations
import sys                     # System-specific parameters and functions
import time
import threading
import shutil
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


if __name__ == '__main__':
    # ---------------------- GUI / Widgets ----------------------
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

    # ---------------------- Paths / Config ----------------------
    gConfigPath: Path = None
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
    gUpdateCheckBoxes = {}
    gCustomExe = False
    gMap_rating_matrix = load_map_ratings_matrix()
    gNewDownloadMaps = None
    gNewLocalMaps = None
    gOnlineServers = None
    gPlayersInGame = None

    # ---------------------- GitHub / Version info ----------------------
    gGitHubBranch = "main"
    gGitHubOwner = "ageekhere"
    gGitHubRepo = "Definitive-SMR-Launcher"
    gGitHubVersion: str = "version1.03"
    gVersion: str = "1.03"
    ginternetArchiveIdentifier = "sid-meiers-railroads-custom-maps-collection"

    # ---------------------- Fonts / Geometry ----------------------
    gAppHeight = 720
    gAppWidth = 1280
    gMain_font = ctk.CTkFont(family="arial", size=19, weight="bold")

    # ---------------------- Debug / Logging ----------------------
    gDebug: bool = False
    gLogs: list = []

    # ---------------------- Initialization ----------------------
    error_logs("[Main] Welcome to Definitive-SMR-Launcher", "info")
    error_logs(f"[Main] Python version: {sys.version}")

    ctk.deactivate_automatic_dpi_awareness()
    error_logs("[Main] Disabled DPI awareness", "info")

    ctk.set_appearance_mode("dark")
    error_logs("[Main] set_appearance_mode to Dark", "info")

    ctk.set_default_color_theme("blue")
    error_logs("[Main] set_default_color_theme to blue", "info")

    # Splash screen
    create_splash()

    gApp.resizable(0, 0)

    # User config
    make_config()
    gApp.title("Definitive SMR Launcher - " + str(gVersion))

    # Center window
    mainWindowX = (gApp.winfo_screenwidth() - gAppWidth) // 2
    mainWindowY = (gApp.winfo_screenheight() - gAppHeight) // 6
    gApp.geometry(f"{gAppWidth}x{gAppHeight}+{mainWindowX}+{mainWindowY}")

    gIcon = create_icon(sys, gApp)

    if get_config_value("enableopenspy") == "1":
        gCustomExe = True

    # ---------------------- Background Image ----------------------
    if getattr(sys, 'frozen', False):
        bg_image_path = os.path.join(sys._MEIPASS, "background.jpg")
        error_logs("[Main] Background path " + str(bg_image_path), "info")
    else:
        bg_image_path = gBackGroundImageUrl
        error_logs("[Main] Background path " + str(bg_image_path), "info")

    try:
        bg_image = Image.open(bg_image_path)
        error_logs("[Main] Loading background Image Successful", "info")
    except FileNotFoundError as e:
        error_logs("[Main] Loading background Image Failed " + str(e), "error")
        sys.exit(1)

    gInterface_canvas = ctk.CTkCanvas(gApp, highlightthickness=0, bg='black')
    gInterface_canvas.pack(fill="both", expand=True)

    bg_image = bg_image.resize((gAppWidth, gAppHeight))
    bg_photo = ImageTk.PhotoImage(bg_image)
    gInterface_canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # ---------------------- User Paths ----------------------
    shell = win32com.client.Dispatch("WScript.Shell")

    gUsermap_path = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "UserMaps"
    error_logs("[Main]  UserMaps path: " + str(gUsermap_path), "info")

    gCustomAssets_path = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "CustomAssets"
    error_logs("[Main]  CustomAssets path: " + str(gCustomAssets_path), "info")

    gGameDocs = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads"
    error_logs("[Main]  MyDocuments path to Sid Meier's Railroads: " + str(gGameDocs), "info")

    # ---------------------- Scrollable Frame ----------------------
    gScrollable_frame = ctk.CTkScrollableFrame(gInterface_canvas, corner_radius=0, width=1035, height=gAppHeight)
    gScrollable_frame.place(x=230)

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

    # ---------------------- Managers / Watchers ----------------------
    interface_manager(os, ctk)
    github_update()
    main_watcher()
    update_maps_timer()
    check_openspy()  # Uncomment if needed

    # ---------------------- Run App ----------------------
gApp.mainloop()
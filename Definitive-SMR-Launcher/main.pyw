# --- Standard Library Imports ---
import sys                     # System-specific parameters and functions
import os                      # File system operations
#import shutil                  # High-level file operations (copy, move, delete)
from pathlib import Path        # Object-oriented filesystem paths
from functools import partial   # Pass arguments into callbacks
from threading import Thread, Event  # Multithreading support
from ctypes import windll       # Windows API access (e.g., DPI awareness)
import time

# --- Third-Party Libraries ---
import customtkinter as ctk     # Modern themed Tkinter GUI
from tkinter import filedialog  # File/directory selection dialogs
from PIL import Image, ImageTk  # Image handling and displaying in Tkinter
import imageio                  # Read/write a wide range of image formats
import requests                 # HTTP requests (download files, APIs)
import pyzipper                 # Advanced ZIP handling (e.g., AES encryption)
import win32com.client          # Windows COM automation (shortcuts, Office, etc.)
import py7zr
import tkinter as tk

from configparser import ConfigParser
import threading

from error_logs import error_logs
from debug_window import debug_window
from create_splash import create_splash
from config_manager import read_write_config, make_config, get_config_value, set_config_value
from create_icon import create_icon
from create_symlink import create_symlink
from map_manager import map_manager
from interface_manager import interface_manager

from string_utils import string_utils
from game_launcher import game_launcher

from map_info_manager import map_info_manager
from map_checker import map_checker
from map_updater import map_updater
from map_downloader import map_downloader
from map_update_worker import map_update_worker
from map_extractor import map_extractor
from map_download_extract import map_download_extract
from custom_exe_manager import custom_exe_manager
from file_operations import file_operations
from difficulty_manager import difficulty_manager
from archive_maps import archive_maps
from set_game_type_selection import set_game_type_selection
from gamepath_manager import gamepath_manager
from github_update import github_update

def stopThread():
    print("thread")
    gStopDownload.set()
    time.sleep(1.0)
if __name__ == '__main__': 
    gDebug:bool = False # Displays the logs to the console 
    gLogs:list = [] # Saves all the logs to a list
    gLogWindow = None # Log window
    gLogWindowTextbox = "" # Log textbox that is updated throughout the project

    error_logs("[Main] Welcome to Definitive-SMR-Launcher","info")
    
    ctk.deactivate_automatic_dpi_awareness() # Disable DPI scaling
    error_logs("[Main] Disabled DPI awareness","info")
    ctk.set_appearance_mode("dark") # Set to use appearance mode for light and dark themes
    error_logs("[Main] set_appearance_mode to Dark","info")
    ctk.set_default_color_theme("blue") # Set color theme to blue
    error_logs("[Main] set_default_color_theme to blue","info")

    create_splash() # Create a splash screen

    gApp: ctk.CTk = ctk.CTk() # Using theme ctk
    gApp.resizable(0,0) # disable window resizing

    # GitHub repo details or connecting to github for updates
    gGitHubOwner = "ageekhere"
    gGitHubRepo = "Definitive-SMR-Launcher"
    gGitHubBranch = "main"

    # Internet Archive
    ginternetArchiveIdentifier = "sid-meiers-railroads-custom-maps-collection"

    gVersion:str = "1.00" # App version
    gGitHubVersion:str = "version1.00"
    gBackGroundImageUrl:str = r"interface\background.jpg"
    gCustom_difficulty = None
    gCustom_exe = None
    gScrollable_frame = None
    gDownloadThread = None
    gStopDownload = threading.Event()
    gUsermap_path = None
    gCustomAssets_path = None
    gGameDocs = None
    gSelected_button = None
    gGameLocation_label = None
    gCustomExe = False
    gAppWidth = 1280 
    gAppHeight = 720
    gMain_font = ctk.CTkFont(family="arial", size=19,weight="bold")
    gUpdate_maps_button = None
    gStart_button = None
    gNewDownloadMaps = None
    gNewLocalMaps = None
    gConfigPath:Path = None
    gConfigUserData:ConfigParser = None
    gConfigUserInfo = None
    gGamePath:str = "" # stores the current game path
    gGameTypeDrop = None
    gCustom_exe_button = None
    gDownloadList = None
    gSelected_option = ctk.StringVar(value="Not selected")  # default value
    gInstallLogTextbox = None
    gUpdateCheckBoxes = {}
    gCustom_levels_button = None
    gLog_button = None
    gGamepath_button = None
    gCancel_button = None
    gRemoveSymlink = None
    make_config() # Setup the user config file
    gApp.title("Definitive SMR Launcher - " + str(gVersion)) # Set title of the app
    mainWindowX = (gApp.winfo_screenwidth() - gAppWidth) // 2 # Use to center the app windows along X
    mainWindowY = (gApp.winfo_screenheight() - gAppHeight) // 6 # Use to center the app windows along Y
    gApp.geometry(f"{gAppWidth}x{gAppHeight}+{mainWindowX}+{mainWindowY}") # Set the app geometry so that it is centered 
    create_icon(sys) # Create an icon for the app

    if getattr(sys, 'frozen', False): # Running as a PyInstaller bundle
        bg_image_path = os.path.join(sys._MEIPASS, "background.jpg")
        error_logs("[Main] Background path " + str(bg_image_path),"info")
    else: # Running as a script
        bg_image_path = gBackGroundImageUrl
        error_logs("[Main] Background path " + str(bg_image_path),"info")
    try: # Open the background image
        bg_image = Image.open(bg_image_path)
        error_logs("[Main] Loading background Image Successful","info")
    except FileNotFoundError as e:
        error_logs("[Main] Loading background Image Failed " + str(e),"error")
        sys.exit(1)

    gInterface_canvas = ctk.CTkCanvas(gApp, highlightthickness=0,bg='black') # Create the new interface canvas
    gInterface_canvas.pack(fill="both", expand=True) # Add the canvas to the app

    bg_image = bg_image.resize((gAppWidth, gAppHeight)) # Resize to match window size
    bg_photo = ImageTk.PhotoImage(bg_image) # Convert to Tkinter-compatible format
    gInterface_canvas.create_image(0, 0, image=bg_photo, anchor="nw") # Place the background image onto the canvas

    # Set the MyDocuments folder
    shell = win32com.client.Dispatch("WScript.Shell")
    gUsermap_path = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "UserMaps"
    error_logs("[Main]  UserMaps path: " + str(gUsermap_path),"info")

    gCustomAssets_path = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "CustomAssets"
    error_logs("[Main]  CustomAssets path: " + str(gCustomAssets_path),"info")
    gGameDocs = Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads"
    error_logs("[Main]  MyDocuments path to Sid Meier's Railroads: " + str(gGameDocs),"info")

    # Create a scrollable frame for the maps
    gScrollable_frame = ctk.CTkScrollableFrame(gInterface_canvas,corner_radius=0,width=1035,height=gAppHeight)
    gScrollable_frame.place(x=230) # Align to the right (top-right corner)

    try:
        import pyi_splash
        pyi_splash.close()
        error_logs("[close_splash] Splash screen closed", "info")
    except ImportError:
        error_logs("[close_splash] No splash to close", "warning")
    
    maps_dir_path = Path(os.getcwd()) / "maps"
    maps_dir_path.mkdir(parents=True, exist_ok=True)
    download_dir_path = Path(os.getcwd()) / "downloads"
    download_dir_path.mkdir(parents=True, exist_ok=True)

    interface_manager(os,ctk)

    github_update()
    gApp.mainloop()





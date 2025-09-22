"""
game_launcher.py

Handles launching the RailRoads game with optional OpenSpy LAA exe.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports
from ctypes import windll

def game_launcher():
    """
    Launch the RailRoads game executable, optionally using OpenSpy LAA exe.

    Uses:
        __main__.gCustomExe (bool): Whether to use custom exe.
        __main__.gConfigUserInfo (dict): Config section for gametype.
        __main__.gGamePath (str): Path to game installation.
        debug: Logger function.

    Notes:
        Uses ShellExecuteW to run as administrator.
    """
    runexe = "RailRoads.exe"

    # Check if user wants to use custom OpenSpy exe
    if getattr(__main__, "gCustomExe", False):
        gametype = __main__.get_config_value("USERINFO", "gametype") or "Steam"
        if gametype == "Steam":
            runexe = "RailRoads_Steam_LAA_OpenSpy.exe"
        else:
            runexe = "RailRoads_LAA_OpenSpy.exe"

    __main__.error_logs(f"[game_launcher] Launching game from path: {__main__.gGamePath}", "info")
    __main__.error_logs(f"[game_launcher] Executable: {runexe}", "info")

    exe_path = __main__.os.path.join(__main__.gGamePath, runexe)

    try:
        ret = windll.shell32.ShellExecuteW(None, "runas", exe_path, None, None, 1)
        if ret <= 32:
            __main__.error_logs("[game_launcher] Cannot start game", "error")
    except Exception as e:
        __main__.error_logs(f"[game_launcher] Error starting game: {e}", "error")
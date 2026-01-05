"""
game_launcher.py

Handles launching the RailRoads game with optional OpenSpy LAA exe.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports

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
    if (__main__.gCustomExe == True):
        gametype = __main__.get_config_value("gametype")
        if gametype == "Steam":
            runexe = "RailRoads_Steam_LAA_OpenSpy.exe"
        else:
            runexe = "RailRoads_LAA_OpenSpy.exe"

    __main__.error_logs(f"[game_launcher] Launching game from path: {__main__.gGamePath}", "info")
    __main__.error_logs(f"[game_launcher] Executable: {runexe}", "info")

    exe_path = __main__.os.path.join(__main__.gGamePath, runexe)

    # Check if file exists
    if not __main__.os.path.isfile(exe_path):
        __main__.error_logs(f"[game_launcher] File not found: {exe_path}", "error")
        return

    workdir = __main__.os.path.dirname(exe_path)

    try:
        ret = __main__.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, workdir, 1)

        # Log the return code
        __main__.error_logs(f"[game_launcher] ShellExecute return code: {ret}", "info")

        if ret <= 32:
            __main__.error_logs(f"[game_launcher] Cannot start game, error code {ret}", "error")
            return

    except Exception as e:
        __main__.error_logs(f"[game_launcher] Error starting game: {e}", "error")
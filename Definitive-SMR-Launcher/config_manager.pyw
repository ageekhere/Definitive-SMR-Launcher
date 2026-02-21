import __main__ # Import the __main__ module so we can access variables and functions defined in the main script
from error_logs import error_logs
from pathlib import Path
from configparser import ConfigParser

gConfigPath = None
gConfigUserData = None

def read_write_config(fileAction: str) -> None:
    """
    Read or write the INI config file.

    Args:
        fileAction (str): "r" to read from config file, "w" to write config file.

    Globals used (from __main__):
        gConfigPath (Path): Path to the config.ini file.
        gConfigUserData (ConfigParser): Holds INI file data.

    Raises:
        ValueError: If fileAction is not "r" or "w".
    """
    global gConfigPath
    global gConfigUserData
    error_logs("[read_write_config] accessing config file", "info")

    if fileAction not in ("r", "w"):
        error_logs("[read_write_config] invalid input option", "error")
        raise ValueError("Invalid option: must be 'r' or 'w'")

    try:
        if fileAction == "w":
            # Ensure the parent folder (e.g., "config/") exists before writing
            gConfigPath.parent.mkdir(parents=True, exist_ok=True)

            with open(gConfigPath, "w") as pConfigfile:
                gConfigUserData.write(pConfigfile)
                error_logs(f"[read_write_config] Successfully wrote to {gConfigPath}", "info")

        elif fileAction == "r":
            gConfigUserData.read(gConfigPath)
            error_logs(f"[read_write_config] Successfully read from {gConfigPath}", "info")

    except PermissionError:
        error_logs(f"[read_write_config] Permission denied: {gConfigPath}", "error")
    except FileNotFoundError:
        error_logs(f"[read_write_config] File not found: {gConfigPath}", "error")
    except Exception as e:
        error_logs(f"[read_write_config] Cannot access {gConfigPath}: {e}", "error")

def make_config() -> None:
    """
    Create or load the user configuration file (config/config.ini).
    If the file does not exist, a new one with default values is created.

    Globals updated (in __main__):
        gConfigUserData (ConfigParser): Stores config data.
        gConfigPath (Path): Path to the config file.
        gConfigUserInfo (SectionProxy): USERINFO section of config.
        gGamePath (str): Game path location.
    """
    global gConfigPath
    global gConfigUserData
    error_logs("[make_config] Setting up user config.ini", "info")

    gConfigUserData = ConfigParser()
    gConfigPath = Path("config/config.ini")

    try:
        if gConfigPath.is_file():
            error_logs("[make_config] config.ini exists, reading file", "info")
            read_write_config("r")
        else:
            error_logs("[make_config] creating new config.ini with defaults", "info")
            gConfigUserData["USERINFO"] = {
                "gamepath": __main__.gGamePath,
                "customdifficulty": "0",
                "enableopenspy": "0",
                "lastupdate": "na",
                "updatelastcheck": "",
                "gametype": "Steam",
                "option1": "",
                "option2": "",
                "option3": "",
                "option4": "",
                "option5": "",
                "option6": "",
                "option7": "",
                "option8": "",
                "option9": "",
                "option10": ""
            }

        # Save defaults (if new) and reload to ensure consistency
        read_write_config("w")
        read_write_config("r")

        # Cache USERINFO section into globals for quick access
        __main__.gConfigUserInfo = gConfigUserData["USERINFO"]
        __main__.gGamePath = __main__.gConfigUserInfo.get("gamepath", "")

    except PermissionError:
        error_logs("[make_config] PermissionError: Could not access config file", "error")
    except FileNotFoundError:
        error_logs("[make_config] FileNotFoundError: Config path not found", "error")
    except OSError as e:
        error_logs(f"[make_config] OSError: {e}", "error")
    except Exception as e:
        error_logs(f"[make_config] Unexpected Exception: {e}", "error")


# -------------------------------------------------------------------
# Helper Functions for config access
# -------------------------------------------------------------------

def get_config_value(key: str, default: str = "") -> str:
    """
    Retrieve a value from the USERINFO section of config.ini.

    Args:
        key (str): The key to look up (e.g., "gamepath").
        default (str, optional): Fallback value if key is missing. Defaults to "".

    Returns:
        str: The value from config or the default.
    """
    try:
        return __main__.gConfigUserInfo.get(key, default)
    except Exception:
        error_logs(f"[get_config_value] Missing key '{key}', returning default='{default}'", "warning")
        return default

def set_config_value(key: str, value: str) -> None:
    """
    Update a value in the USERINFO section of config.ini.

    Args:
        key (str): The key to update (e.g., "gamepath").
        value (str): The new value to assign.

    Side Effects:
        - Updates gConfigUserData and gConfigUserInfo.
        - Persists the change to config/config.ini.
    """
    global gConfigUserData
    try:
        gConfigUserData.set("USERINFO", key, value)
        read_write_config("w")  # Save updated config
        __main__.gConfigUserInfo = gConfigUserData["USERINFO"]  # Refresh
        error_logs(f"[set_config_value] Updated '{key}' to '{value}'", "info")

        # Special case: if updating gamepath, also refresh global gGamePath
        if key == "gamepath":
            __main__.gGamePath = value

    except Exception as e:
        error_logs(f"[set_config_value] Failed to update '{key}': {e}", "error")
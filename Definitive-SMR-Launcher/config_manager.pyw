import __main__ # Import the __main__ module so we can access variables and functions defined in the main script

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
    __main__.error_logs("[read_write_config] accessing config file", "info")

    if fileAction not in ("r", "w"):
        __main__.error_logs("[read_write_config] invalid input option", "error")
        raise ValueError("Invalid option: must be 'r' or 'w'")

    try:
        if fileAction == "w":
            # Ensure the parent folder (e.g., "config/") exists before writing
            __main__.gConfigPath.parent.mkdir(parents=True, exist_ok=True)

            with open(__main__.gConfigPath, "w") as pConfigfile:
                __main__.gConfigUserData.write(pConfigfile)
                __main__.error_logs(f"[read_write_config] Successfully wrote to {__main__.gConfigPath}", "info")

        elif fileAction == "r":
            __main__.gConfigUserData.read(__main__.gConfigPath)
            __main__.error_logs(f"[read_write_config] Successfully read from {__main__.gConfigPath}", "info")

    except PermissionError:
        __main__.error_logs(f"[read_write_config] Permission denied: {__main__.gConfigPath}", "error")
    except FileNotFoundError:
        __main__.error_logs(f"[read_write_config] File not found: {__main__.gConfigPath}", "error")
    except Exception as e:
        __main__.error_logs(f"[read_write_config] Cannot access {__main__.gConfigPath}: {e}", "error")

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
    __main__.error_logs("[make_config] Setting up user config.ini", "info")

    __main__.gConfigUserData = __main__.ConfigParser()
    __main__.gConfigPath = __main__.Path("config/config.ini")

    try:
        if __main__.gConfigPath.is_file():
            __main__.error_logs("[make_config] config.ini exists, reading file", "info")
            read_write_config("r")
        else:
            __main__.error_logs("[make_config] creating new config.ini with defaults", "info")
            __main__.gConfigUserData["USERINFO"] = {
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
        __main__.gConfigUserInfo = __main__.gConfigUserData["USERINFO"]
        __main__.gGamePath = __main__.gConfigUserInfo.get("gamepath", "")

    except PermissionError:
        __main__.error_logs("[make_config] PermissionError: Could not access config file", "error")
    except FileNotFoundError:
        __main__.error_logs("[make_config] FileNotFoundError: Config path not found", "error")
    except OSError as e:
        __main__.error_logs(f"[make_config] OSError: {e}", "error")
    except Exception as e:
        __main__.error_logs(f"[make_config] Unexpected Exception: {e}", "error")


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
        __main__.error_logs(f"[get_config_value] Missing key '{key}', returning default='{default}'", "warning")
        return default

def set_config_value(key: str, value: str) -> None:
    """
    Update a value in the USERINFO section of config.ini.

    Args:
        key (str): The key to update (e.g., "gamepath").
        value (str): The new value to assign.

    Side Effects:
        - Updates __main__.gConfigUserData and gConfigUserInfo.
        - Persists the change to config/config.ini.
    """
    try:
        __main__.gConfigUserData.set("USERINFO", key, value)
        read_write_config("w")  # Save updated config
        __main__.gConfigUserInfo = __main__.gConfigUserData["USERINFO"]  # Refresh
        __main__.error_logs(f"[set_config_value] Updated '{key}' to '{value}'", "info")

        # Special case: if updating gamepath, also refresh global gGamePath
        if key == "gamepath":
            __main__.gGamePath = value

    except Exception as e:
        __main__.error_logs(f"[set_config_value] Failed to update '{key}': {e}", "error")
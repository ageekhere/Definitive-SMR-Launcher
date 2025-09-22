"""
custom_exe_manager.py

Handles enabling or disabling the custom OpenSpy LAA executable for the game.
"""
from config_manager import get_config_value, set_config_value
#from file_operations import file_operations  # Make sure you have this function implemented
import __main__  # Access global variables from main

def custom_exe_manager():
    """
    Enable or disable the custom OpenSpy LAA exe based on the CTkCheckBox variable.

    Updates:
        __main__.gCustomExe (bool): Whether the custom exe is enabled.
    """
    if __main__.gCustom_exe.get() == 1:
        __main__.gCustomExe = True
        __main__.error_logs("[custom_exe_manager] Custom exe enabled", "info")
        __main__.set_config_value("enableopenspy", "1")

        # Copy the appropriate exe to the game folder based on gametype
        gametype = get_config_value("gametype")
        if gametype == "Other":
            __main__.file_operations("RailRoads_LAA_OpenSpy.exe")
            __main__.error_logs("[custom_exe_manager] Using RailRoads_LAA_OpenSpy.exe ", "info")
        else:
            __main__.file_operations("RailRoads_Steam_LAA_OpenSpy.exe")
            __main__.error_logs("[custom_exe_manager] Using RailRoads_Steam_LAA_OpenSpy.exe ", "info")
    else:
        __main__.gCustomExe = False
        __main__.set_config_value("enableopenspy", "0")
        __main__.error_logs("[custom_exe_manager] Custom exe disabled", "info")
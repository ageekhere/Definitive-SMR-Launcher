"""
set_game_type_selection.pyw

Update the game type selection from the dropdown.

Args:
    choice (str): Selected game type ("Steam" or "Other").

Side Effects:
    - Updates config via set_config_value().
    - Updates __main__.gConfigUserInfo["gametype"] automatically via config_manager.
"""
import __main__
def set_game_type_selection(choice: str):
    try:
        # Persist the new value in config.ini and update globals
        __main__.set_config_value("gametype", choice)
        __main__.error_logs(f"[set_game_type_selection] Game type set to: {__main__.gConfigUserInfo['gametype']}", "info")
    except Exception as e:
        __main__.error_logs(f"[set_game_type_selection] Failed to update game type: {e}", "error")
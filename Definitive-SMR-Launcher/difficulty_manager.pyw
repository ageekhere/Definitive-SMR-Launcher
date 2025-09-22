"""
difficulty_manager.py

Manages enabling or disabling custom difficulty XML files for the game.
"""

import shutil
import __main__  # Access global variables from main

def difficulty_manager() -> None:
    """
    Enable or disable custom difficulty levels in RailRoads by copying and renaming XML files.
    Uses __main__.gCustom_difficulty and __main__.gGamePath.
    """
    difficulty_file_source = __main__.os.path.join(".", "DSMRL_data", "RRT_Difficulty.xml")
    game_assets_path = __main__.os.path.join(__main__.gGamePath, "Assets", "XML")
    difficulty_file_game = __main__.os.path.join(game_assets_path, "RRT_Difficulty.xml")
    difficulty_file_backup = __main__.os.path.join(game_assets_path, "RRT_DifficultyBK.xml")

    try:
        if __main__.gCustom_difficulty.get() == 1:
            __main__.error_logs("[difficulty_manager] Enabling custom difficulty", "info")
            __main__.set_config_value("customdifficulty", "1")

            # Create backup if missing
            if __main__.os.path.exists(difficulty_file_game) and not __main__.os.path.exists(difficulty_file_backup):
                shutil.copy(difficulty_file_game, difficulty_file_backup)
                __main__.error_logs(f"[difficulty_manager] Backed up original {difficulty_file_game} to {difficulty_file_backup}","info")

            # Copy custom difficulty into place
            if __main__.os.path.exists(difficulty_file_source):
                shutil.copy(difficulty_file_source, difficulty_file_game)
                __main__.error_logs(
                    f"[difficulty_manager] Copied custom difficulty from {difficulty_file_source} to {difficulty_file_game}","info")
            else:
                __main__.error_logs(f"[difficulty_manager] Source file not found: {difficulty_file_source}","error")

        else:  # disabling
            __main__.set_config_value("customdifficulty", "0")
            __main__.error_logs("[difficulty_manager] Disabling custom difficulty", "info")

            # Restore backup if it exists
            if __main__.os.path.exists(difficulty_file_backup):
                shutil.copy(difficulty_file_backup, difficulty_file_game)
                __main__.error_logs("[difficulty_manager] Restored original difficulty file", "info")
            else:
                __main__.error_logs("[difficulty_manager] No backup found to restore!", "warning")

    except Exception as e:
        __main__.error_logs(f"[difficulty_manager] Error updating difficulty files: {e}", "error")
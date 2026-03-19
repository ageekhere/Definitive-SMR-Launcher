"""
difficulty_manager.py

Manages enabling or disabling custom difficulty XML files for the game.
"""

import hashlib
import __main__

def file_hash(path):
    """Return SHA256 hash of a file."""
    if not __main__.os.path.exists(path):
        return None

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def difficulty_manager() -> None:
    """
    Enable or disable custom difficulty levels in RailRoads by copying and renaming XML files.
    """

    difficulty_file_source = __main__.os.path.join(".", "DSMRL_data", "RRT_Difficulty.xml")
    game_assets_path = __main__.os.path.join(__main__.gGamePath, "Assets", "XML")
    difficulty_file_game = __main__.os.path.join(game_assets_path, "RRT_Difficulty.xml")
    difficulty_file_backup = __main__.os.path.join(game_assets_path, "RRT_DifficultyBK.xml")

    try:
        if __main__.gCustom_difficulty.get() == 1:
            __main__.error_logs("[difficulty_manager] Enabling custom difficulty", "info")
            __main__.set_config_value("customdifficulty", "1")

            # 📦 Create backup if missing
            if (__main__.os.path.exists(difficulty_file_game) and
                not __main__.os.path.exists(difficulty_file_backup)):
                
                __main__.shutil.copy(difficulty_file_game, difficulty_file_backup)
                __main__.error_logs(f"[difficulty_manager] Backed up original to {difficulty_file_backup}","info")

            # 🔍 Only copy if different
            if __main__.os.path.exists(difficulty_file_source):
                src_hash = file_hash(difficulty_file_source)
                dst_hash = file_hash(difficulty_file_game)

                if src_hash == dst_hash:
                    __main__.error_logs("[difficulty_manager] Custom difficulty already applied, skipping copy","info")
                else:
                    __main__.shutil.copy(difficulty_file_source, difficulty_file_game)
                    __main__.error_logs("[difficulty_manager] Copied custom difficulty file","info")
            else:
                __main__.error_logs(f"[difficulty_manager] Source file not found: {difficulty_file_source}","error")

        else:  # 🔄 disabling
            __main__.set_config_value("customdifficulty", "0")
            __main__.error_logs("[difficulty_manager] Disabling custom difficulty", "info")

            if __main__.os.path.exists(difficulty_file_backup):
                src_hash = file_hash(difficulty_file_backup)
                dst_hash = file_hash(difficulty_file_game)

                if src_hash == dst_hash:
                    __main__.error_logs("[difficulty_manager] Original difficulty already restored, skipping","info")
                else:
                    __main__.shutil.copy(difficulty_file_backup, difficulty_file_game)
                    __main__.error_logs("[difficulty_manager] Restored original difficulty file","info")
            else:
                __main__.error_logs("[difficulty_manager] No backup found to restore!","warning")

    except Exception as e:
        __main__.error_logs(f"[difficulty_manager] Error updating difficulty files: {e}","error")
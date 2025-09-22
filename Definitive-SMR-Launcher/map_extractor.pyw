"""
map_extractor.py

Extracts any remaining downloaded map archives that are not yet extracted.
"""

import __main__  # Access main's globals and functions
from pathlib import Path
import py7zr
import time

def map_extractor():
    """
    Extract any files in the downloads directory that are not already in the maps directory.

    Uses globals:
        __main__.gDownloadList

        __main__.gUpdateCheckBoxes
        __main__.map_manager
    """
    __main__.error_logs(f"[map_extractor]", "info")

    try:
        maps_dir = Path(__main__.os.getcwd()) / "maps"
        download_dir = Path(__main__.os.getcwd()) / "downloads"

        for file in download_dir.glob("*.7z"):
            folder_name = file.stem
            __main__.error_logs(f"[map_extractor] folder_name: {folder_name}", "info")

            # Skip files not selected for download
            if folder_name not in __main__.gDownloadList:
                #__main__.error_logs(f"[map_extractor] Skipping {folder_name}, not in install list.", "info")
                continue

            # Skip extraction if folder already exists
            if (maps_dir / folder_name).exists():
                #__main__.error_logs(f"[map_extractor] Skipping leftover {file.name}, folder already exists.", "info")
                continue

            __main__.error_logs(f"[map_extractor] Extracting leftover {file.name}...", "info")

            with py7zr.SevenZipFile(file, mode='r') as archive:
                file_list = archive.list()
                total_size = sum(f.uncompressed for f in file_list)
                extracted_size = 0

                # Update checkbox as extraction progresses
                for f in file_list:
                    extracted_size += f.uncompressed
                    percent = (extracted_size / total_size) * 100

                    # Update checkbox text in main's global dictionary
                    if folder_name in __main__.gUpdateCheckBoxes:
                        __main__.gUpdateCheckBoxes[folder_name].configure(
                            text=f"{folder_name} - {percent:.2f}%"
                        )

                    time.sleep(0.01)  # optional for visible UI update

                # Perform the actual extraction
                archive.extractall(path=maps_dir)

            # After extraction, reset checkbox text to original or completed
            if folder_name in __main__.gUpdateCheckBoxes:
                __main__.gUpdateCheckBoxes[folder_name].configure(
                    text=f"{folder_name} - Done"
                )

    except Exception as e:
        __main__.error_logs(f"[map_extractor] Error extracting files: {e}", "error")
    __main__.error_logs(f"[map_extractor] Finished", "info")
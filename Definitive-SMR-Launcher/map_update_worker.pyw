"""
map_update_worker.py

Handles the background process of downloading and extracting maps.
Intended to be run in a separate thread.
"""

import __main__  # Access main's globals and imports

def map_update_worker():
    __main__.error_logs("[map_update_worker] install list", "info")
    """
    Main update process running in a background thread.

    Uses globals:
        __main__.gDownloadList
        __main__.github_maps
        __main__.map_download_extract
        __main__.map_extractor
    """
    try:
        urls = __main__.archive_maps()

        maps_dir = __main__.Path(__main__.os.getcwd()) / "maps"
        maps_dir.mkdir(exist_ok=True)

        for filename, url in urls:
            folder_name = filename.replace(".7z", "")

            # Skip files not selected for download
            if folder_name not in __main__.gDownloadList:
                #__main__.error_logs(f"[map_update_worker] Skipping {folder_name}, not in download list.", "info")
                continue

            # Check if folder already exists
            if not (maps_dir / folder_name).exists():
                __main__.map_download_extract(url, filename)

        # After processing all files, extract any remaining files
        __main__.map_extractor()

    except Exception as e:
        __main__.error_logs(f"[map_update_worker] Error in download thread: {e}", "error")

    __main__.stopThread()
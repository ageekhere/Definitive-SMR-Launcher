"""
map_downloader.py

Downloads a .7z map archive from a URL and extracts it into the maps directory.
"""

import __main__  # Access main's globals and functions
from pathlib import Path
import requests
import py7zr

def map_download_extract(url: str, filename: str):
    """
    Download a .7z file from the given URL into the downloads directory
    and extract it into the maps directory.

    Uses globals:

        __main__.map_manager
    """
    try:
        # Ensure downloads directory exists
        download_dir = Path(__main__.os.getcwd()) / "downloads"
        download_dir.mkdir(exist_ok=True)
        dest_file = download_dir / filename

        # Download the file with progress
        __main__.error_logs(f"[map_download_extract] Downloading {filename}...", "info")
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        downloaded_size = 0

        with open(dest_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        percent = int(downloaded_size * 100 / total_size)
                        renameFile = filename.replace(".7z", "")

                        if __main__.gStopDownload.is_set():
                            # Close file before removing
                            __main__.gUpdateCheckBoxes[renameFile].configure(
                                text=f"{renameFile} - Canceled")
                            f.close()
                            if __main__.os.path.exists(dest_file):
                                __main__.os.remove(dest_file)
                            return  # Exit worker

                        if renameFile in __main__.gUpdateCheckBoxes:
                            __main__.gUpdateCheckBoxes[renameFile].configure(
                            text=f"{renameFile} - {percent:.2f}%")

        __main__.error_logs(f"[map_download_extract] Downloaded {filename}", "info")

        renameFile = filename.replace(".7z", "")
        __main__.gUpdateCheckBoxes[renameFile].configure(text=f"{renameFile} Extracting...")

        # Extract the file
        maps_dir = Path(__main__.os.getcwd()) / "maps"
        maps_dir.mkdir(exist_ok=True)
        __main__.error_logs(f"[map_download_extract] Extracting {filename}...", "info")


        with py7zr.SevenZipFile(dest_file, mode='r') as archive:
            archive.extractall(path=maps_dir)

        __main__.error_logs(f"[map_download_extract] Extracted {filename} into {maps_dir}", "info")

        # Refresh the map interface
        __main__.map_manager()
        __main__.gUpdateCheckBoxes[renameFile].configure(text=f"{renameFile} Done")

    except Exception as e:
        __main__.error_logs(f"[map_download_extract] Error processing {filename}: {e}", "error")
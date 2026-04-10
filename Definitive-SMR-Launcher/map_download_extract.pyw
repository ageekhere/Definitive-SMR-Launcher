"""
map_downloader.py

Downloads a .7z map archive from a URL and extracts it into the maps directory.
Handles both "flat" archives and archives with pre-existing subfolders.
"""

import __main__  # Access main's globals and functions

def map_download_extract(url: str, filename: str):
    """
    Download a .7z file from the given URL into the downloads directory
    and extract it into the maps directory.

    Uses globals:
        __main__.map_manager
        __main__.Path
        __main__.os
        __main__.requests
        __main__.py7zr
        __main__.error_logs
        __main__.gStopDownload
        __main__.gUpdateCheckBoxes
    """
    try:
        # Ensure downloads directory exists
        download_dir = __main__.Path(__main__.os.getcwd()) / "downloads"
        download_dir.mkdir(exist_ok=True)

        reName = filename.split("/")[-1]
        dest_file = download_dir / reName

        # Download the file with progress
        __main__.error_logs(f"[map_download_extract] Downloading {filename}...", "info")
        r = __main__.requests.get(url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        download_size_accumulated = 0

        with open(dest_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    download_size_accumulated += len(chunk)

                    if total_size > 0:
                        percent = (download_size_accumulated * 100) / total_size
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

        # Prepare for extraction
        renameFile = filename.replace(".7z", "")
        __main__.gUpdateCheckBoxes[renameFile].configure(text=f"{renameFile} Extracting...")

        maps_dir = __main__.Path(__main__.os.getcwd()) / "maps"
        maps_dir.mkdir(exist_ok=True)
        
        __main__.error_logs(f"[map_download_extract] Analyzing and Extracting {filename}...", "info")

        with __main__.py7zr.SevenZipFile(dest_file, mode='r') as archive:
            # Inspect the contents of the archive
            all_names = archive.getnames()
            
            # Logic: Check if any file/folder in the archive starts with "MapName/"
            # This indicates the archive already has the required subfolder structure.
            has_root_folder = any(
                name.startswith(f"{renameFile}/") or name.startswith(f"{renameFile}\\") 
                for name in all_names
            )

            if has_root_folder:
                # Case A: Archive has the folder. Extract directly to /maps/
                extraction_path = maps_dir
                __main__.error_logs(f"[map_download_extract] Folder structure detected. Extracting to {maps_dir}", "info")
            else:
                # Case B: Archive is flat. Extract to /maps/MapName/
                extraction_path = maps_dir / renameFile
                extraction_path.mkdir(exist_ok=True)
                __main__.error_logs(f"[map_download_extract] Flat archive detected. Creating folder: {extraction_path}", "info")

            archive.extractall(path=extraction_path)

        __main__.error_logs(f"[map_download_extract] Successfully extracted {filename}", "info")

        __main__.gUpdateCheckBoxes[renameFile].configure(text=f"{renameFile} Done")

    except Exception as e:
        __main__.error_logs(f"[map_download_extract] Error processing {filename}: {e}", "error")
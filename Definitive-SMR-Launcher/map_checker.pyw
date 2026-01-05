"""
map_checker.py

Checks for missing maps, either online (need download) or local (downloaded but not extracted).
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports

def map_checker():
    __main__.error_logs("[map_checker] Checking for map updates" , "info")
    urls = __main__.archive_maps()

    maps_dir_path = __main__.Path(__main__.os.getcwd()) / "maps"
    download_dir_path = __main__.Path(__main__.os.getcwd()) / "downloads"

    # Downloaded .7z filenames without extension
    downloaded_files = [f.stem for f in download_dir_path.glob("*.7z")]

    # --- Online check loop: missing maps that need download ---
    urls_to_download = []
    for filename, url in urls:
        map_name = filename.replace(".7z", "")
        folder_exists = (maps_dir_path / map_name).exists()
        downloaded = map_name in downloaded_files

        if not folder_exists and not downloaded:
            urls_to_download.append((map_name, url))

    # --- Local check loop: already downloaded but not extracted ---
    files_to_extract = []

    for downloaded_name in downloaded_files:
        folder_exists = (maps_dir_path / downloaded_name).exists()
        if not folder_exists:
            # Find the URL for reference
            matching_url = next((url for fname, url in urls if fname.replace(".7z", "") == downloaded_name),None)
            files_to_extract.append((downloaded_name, matching_url))

    # Store globals
    __main__.gNewDownloadMaps = urls_to_download
    __main__.gNewLocalMaps = files_to_extract

    if not urls_to_download and not files_to_extract:
        __main__.gUpdate_maps_button.configure(state="disabled")
        __main__.error_logs("[map_checker] No New maps to download " , "info")
    else:
        __main__.gUpdate_maps_button.configure(state="normal")
        
        
    return urls_to_download, files_to_extract
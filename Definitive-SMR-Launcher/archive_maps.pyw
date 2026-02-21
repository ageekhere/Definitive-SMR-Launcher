from error_logs import error_logs
from map_checker import map_checker
import requests
import threading

_archive_thread = None # Thread
_urls = None

"""
Check for map updates in a thread
"""
MAX_TIMEOUT = 10
def archive_maps(identifier):
    global _archive_thread
    # Check if the thread exists and is currently working
    if _archive_thread is not None and _archive_thread.is_alive():
        error_logs(f"[archive_maps] Fetch already in progress for {identifier}. Ignoring request.", "info")
        return _urls # Exit the function early

    def wrapper():
        try:
            archive_maps_thread(identifier)
        except Exception as e:
            error_logs(f"[archive_maps[wrapper]] Background thread failed: {e}", "error")

    _archive_thread = threading.Thread(target=wrapper, daemon=True) #Create the thread with the wrapper
    _archive_thread.start() #Start the thread
    error_logs(f"[archive_maps] Started new thread for identifier: {identifier}", "info")
    return _urls

"""
Fetches metadata from Internet Archive for the given identifier
and returns a list of downloadable .7z files.
"""
def archive_maps_thread(identifier):
    global _urls
    api_url = f"https://archive.org/metadata/{identifier}" # Build the Internet Archive metadata API URL
    base_download_url = f"https://archive.org/download/{identifier}"
    error_logs(f"[archive_maps] api_url: {api_url} base_download_url:{base_download_url}", "info")
    try: # Send a GET request to the Internet Archive API
        error_logs("[archive_maps] Connecting to archive.org","info")
        resp = requests.get(api_url, timeout=MAX_TIMEOUT) # Request with a timeout
        error_logs("[archive_maps] Collecting resp","info")
        resp.raise_for_status() # Raise an exception if the HTTP status is not 200 OK
        data = resp.json() # Parse the JSON response into a Python dictionary
        error_logs("[archive_maps] Collecting data from resp","info")
    except requests.exceptions.RequestException as e:
        error_logs(f"[archive_maps] Connection error: {e}", "error")
        return []
    except Exception as e:
        error_logs(f"[archive_maps] JSON decoding failed: {e}", "error")
        return [] # Return an empty list if something goes wrong
    # Using a list comprehension
    _urls = [
        (fileinfo["name"], f"{base_download_url}/{fileinfo['name']}")
        for fileinfo in data.get("files", [])
        if fileinfo.get("name", "").lower().endswith(".7z")
    ]
    error_logs(f"[archive_maps] Found {len(_urls)} .7z files for {identifier}", "info")
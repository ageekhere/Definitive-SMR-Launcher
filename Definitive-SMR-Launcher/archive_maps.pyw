from error_logs import error_logs  # Custom logging utility for tracking errors and info messages
from map_checker import map_checker  # Custom utility to check or process the maps once downloaded
import requests  # Main HTTP library for making API requests
from requests.adapters import HTTPAdapter  # Tool to attach retry strategies to specific URL domains
from urllib3.util import Retry  # Configuration utility for backoff and maximum retry attempts
import threading  # Module to offload network-heavy API requests to a background thread

_archive_thread: threading.Thread | None = None  # Global tracker for the active background thread instance
_urls: list[tuple[str, str]] | None = None  # Global storage for the latest list of extracted file tuples (name, download_url)
_connectTimeout: int = 5  # Time (in seconds) allowed to establish a connection to archive.org
_readTimeout: int = 50  # Time (in seconds) to wait for data before throwing a timeout error

archive_session: requests.Session = requests.Session()  # Persistent session to reuse TCP connections for efficiency

retries: Retry = Retry(
    total=3,  # Maximum number of retry attempts before failing completely
    backoff_factor=2,  # Wait times between retries escalate exponentially (2s, 4s, 8s)
    status_forcelist=[429, 500, 502, 503, 504],  # Automatically retry on rate limits or server errors
    raise_on_status=False  # Prevents crashing early so raise_for_status() can handle the errors
)

archive_session.mount("https://", HTTPAdapter(max_retries=retries))  # Apply retry rules to all HTTPS requests


def archive_maps(identifier: str) -> list[tuple[str, str]] | None:
    global _archive_thread
    
    if _archive_thread is not None and _archive_thread.is_alive():  # Block duplicate requests if thread is currently active
        error_logs(f"[archive_maps] Fetch already in progress for {identifier}. Ignoring request.", "info")
        return _urls  # Return the last known URLs state immediately to avoid race conditions

    def wrapper() -> None:
        try:
            archive_maps_thread(identifier)  # Trigger the actual data fetching function
        except Exception as e:
            error_logs(f"[archive_maps[wrapper]] Background thread failed: {e}", "error")  # Catch unexpected thread crashes

    _archive_thread = threading.Thread(target=wrapper, daemon=True)  # Create background thread (daemon auto-closes on exit)
    _archive_thread.start()  # Spin up the background thread asynchronously
    error_logs(f"[archive_maps] Started new thread for identifier: {identifier}", "info")
    return _urls  # Returns current state (may be old/None until the background thread finishes)


def archive_maps_thread(identifier: str) -> list[tuple[str, str]] | None:
    global _urls
    
    api_url: str = f"https://archive.org/metadata/{identifier}"  # Build the Internet Archive metadata API endpoint
    base_download_url: str = f"https://archive.org/download/{identifier}"  # Build the root directory URL where files are hosted
    error_logs(f"[archive_maps_thread] api_url: {api_url} base_download_url:{base_download_url}", "info")
    
    try:
        error_logs("[archive_maps_thread] Connecting to archive.org", "info")
        resp: requests.Response = archive_session.get(api_url, timeout=(_connectTimeout, _readTimeout))  # Execute HTTP GET with timeouts
        error_logs("[archive_maps_thread] Collecting resp", "info")
        resp.raise_for_status()  # Throw an HTTPError if the server returned a bad status code (e.g., 404)
        data: dict = resp.json()  # Parse raw string response into a Python dictionary
        error_logs("[archive_maps_thread] Collecting data from resp", "info")
        
    except requests.exceptions.Timeout as e:
        error_logs(f"[archive_maps_thread] Request timed out after retries: {e}", "error")  # Failed after all retries exhausted
        return []
    except requests.exceptions.RequestException as e:
        error_logs(f"[archive_maps_thread] Connection error: {e}", "error")  # Catch generic network drops, DNS issues, etc.
        return []
    except Exception as e:
        error_logs(f"[archive_maps_thread] JSON decoding failed: {e}", "error")  # Catch issues if API returns plain HTML or bad JSON
        return [] 
        
    _urls = [  # Extract matching .7z files using a list comprehension
        (fileinfo["name"], f"{base_download_url}/{fileinfo['name']}")
        for fileinfo in data.get("files", [])  # Use .get() safely to prevent KeyErrors if "files" doesn't exist
        if fileinfo.get("name", "").lower().endswith(".7z")  # Filter for .7z files specifically
    ]
    
    map_checker()  # Run external validation utility on the fresh URLs list
    error_logs(f"[archive_maps_thread] Found {len(_urls)} .7z files for {identifier}", "info")
    return _urls  # Return the newly populated list of URLs
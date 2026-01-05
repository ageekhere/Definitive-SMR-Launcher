"""
map_downloader.py

Starts the map download process in a separate thread and updates the UI status.
"""
import __main__  # Access main's globals and imports

def map_downloader():
    """
    Initiates the download process for maps.
    
    Uses globals:
        __main__.gDownloadThread

        __main__.gApp
        __main__.map_update_worker
        __main__.map_manager
    """
    try:
        # Refresh map interface before starting download
        __main__.map_manager()

        __main__.gStopDownload.clear()
        # Start the download thread
        __main__.gDownloadThread = __main__.Thread(target=__main__.map_update_worker, daemon=True)

        # Schedule thread start via CTk mainloop
        __main__.gApp.after(0, __main__.gDownloadThread.start)

        __main__.error_logs("[map_downloader] Starting map download/install", "info")

    except Exception as e:
        __main__.error_logs(f"[map_downloader] Failed to start map download: {e}", "error")

from watchdog.observers import Observer       # Watches filesystem events
from watchdog.events import FileSystemEventHandler  # Base class for handling events
import __main__                              # Access shared globals / app state

# Directory to watch for map changes
maps_dir = __main__.Path(__main__.os.getcwd()) / "maps"

# Timer used to debounce filesystem events
_stability_timer = None

# How long the filesystem must be idle before we react
STABLE_DELAY = 1.0  # seconds without changes


def reload(event):
    """
    Called after the filesystem becomes stable.
    Rebuilds the map UI.
    """
    if event.event_type == "deleted":
        __main__.gSelected_button = None
        for widget in __main__.gScrollable_frame.winfo_children():
            widget.destroy()
    __main__.map_manager()

def on_maps_changed(event):
    """
    Called for every filesystem event (file/folder add, remove, modify).
    Uses a debounce timer so actions only happen after copying is finished.
    """
    global _stability_timer

    # Cancel any previously scheduled reload
    # This prevents triggering while files are still copying
    if _stability_timer:
        _stability_timer.cancel()

    # Remove any existing symlinks before rebuilding maps
    for path in __main__.gGameDocs.rglob("*"):
        if path.is_symlink():
            __main__.error_logs(f"Removing symlink: {path}", "info")
            path.unlink()
            __main__.gRemoveSymlink.configure(state="disabled")

    # Start (or restart) the stability timer
    _stability_timer = __main__.threading.Timer(
        STABLE_DELAY,
        # IMPORTANT:
        # Use reload (function reference), NOT reload()
        lambda: __main__.gApp.after(0, reload,event)
    )

    _stability_timer.daemon = True
    _stability_timer.start()


class MapsHandler(FileSystemEventHandler):
    """
    Watchdog event handler that triggers on ANY filesystem event.
    """
    def on_created(self, event):
        on_maps_changed(event)

    #def on_modified(self, event):
        #on_maps_changed(event)

    def on_deleted(self, event):
        on_maps_changed(event)

def main_watcher():
    """
    Starts the watchdog observer for the maps directory.
    Should be called once when the app starts.
    """
    handler = MapsHandler()
    observer = Observer()

    # recursive=False means:
    # - Detect new folders
    # - Detect file changes in maps/
    # - NOT detect changes inside subfolders
    observer.schedule(handler, str(maps_dir), recursive=False)

    observer.daemon = True  # Stop observer when app exits
    observer.start()

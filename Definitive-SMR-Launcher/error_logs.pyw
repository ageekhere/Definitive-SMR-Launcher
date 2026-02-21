# logger.pyw
import __main__

def error_logs(message: str, level: str = "info"):
    MAX_LOGS = 1000
    """
    Append a message to the main log with color coding and optional debug printing.

    Args:
        message (str): The log message.
        level (str): Log level: "info", "warning", "error". Default is "info".
    """

    # --- Debug print ---
    if getattr(__main__, "gDebug", True):
        print(f"[{level.upper()}] {message}")

    # --- Map log levels to colors ---
    color_map = {
        "info": "green",
        "warning": "yellow",
        "error": "red"
    }
    color = color_map.get(level.lower(), "green")

    # --- Ensure gLogs exists ---
    if not hasattr(__main__, "gLogs") or __main__.gLogs is None:
        __main__.gLogs = []

    # --- Update UI button for errors safely ---
    try:
        log_button = getattr(__main__, "gLog_button", None)
        if log_button is not None and level.lower() == "error":
            log_button.configure(fg_color="red", hover_color="#cc0000")
    except Exception:
        pass  # ignore if UI not initialized yet

    # --- Append to gLogs ---
    __main__.gLogs.append((message, color))
    if len(__main__.gLogs) > MAX_LOGS:
        for i, (_, c) in enumerate(__main__.gLogs):
            if c == "green":
                __main__.gLogs.pop(i)
                break
        else:
            # If no green found, remove oldest entry
            __main__.gLogs.pop(0)

    # --- Update log window safely ---
    #try:
    #    if getattr(__main__, "gLogWindow", None) is not None:
    #        __main__.debug_window()
    #except Exception:
    #    pass
    safe_update_log_window()
# --- Update log window safely, max once per second ---
def safe_update_log_window():
    try:
        now = __main__.time.time()
        last = getattr(__main__, "_last_log_update", 0)
        if now - last >= 1:  # 1 second has passed
            __main__._last_log_update = now
            if getattr(__main__, "gLogWindow", None) is not None:
                __main__.debug_window()
    except Exception:
        pass
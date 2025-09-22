#logger.pyw
import __main__

def error_logs(message: str, level: str = "info"):
    """
    Append a debug message to the global gLogs string in the main script.

    This function does not keep its own copy of gLogs. Instead, it directly
    modifies the variables defined in the __main__ module.

    Args:
        errorMessage (str): The message to append to the log.
    """

    # Import the __main__ module so we can access variables defined there
    # (__main__ is the special name Python assigns to the top-level script).
    
    # Check if debugging is enabled in the main script by looking for gDebug.
    # If gDebug is True, print the log.
    if getattr(__main__, "gDebug", True):
        print(message)

    # Map log levels to colors
    color_map = {
        "info": "green",
        "warning": "yellow",
        "error": "red"
    }
    color = color_map.get(level.lower(), "green")

    # Initialize gLogs if it doesn't exist
    if not hasattr(__main__, "gLogs"):
        __main__.gLogs = []

    if hasattr(__main__, "gLog_button") and __main__.gLog_button is not None and level == "error":
        __main__.gLog_button.configure(fg_color="red", hover_color="#cc0000")

    # Append the message to gLogs in the main script, followed by a newline.
    __main__.gLogs.append((message, color))
    if(__main__.gLogWindow != None):
        __main__.debug_window()
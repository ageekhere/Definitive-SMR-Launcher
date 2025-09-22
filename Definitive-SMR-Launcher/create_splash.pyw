# splashScreen.pyw
import sys
from error_logs import error_logs 
def create_splash():
    """
    Show a splash screen if the program is running as a frozen executable.

    This function logs each step via the error_logs() function from logger.py.
    - If running from a PyInstaller/auto-py-to-exe EXE, it attempts to
      import pyi_splash to display the splash.
    - If running in normal Python, it logs that no splash is available.

    The function does not return anything; all messages are sent to error_logs().
    """

    # Log that the splash screen is starting to load
    error_logs("[create_splash] Loading splash screen", "info")

    # getattr(sys, 'frozen', False) returns True if the script is running
    # from a bundled executable (PyInstaller / auto-py-to-exe).
    if getattr(sys, 'frozen', False):
        try:
            # Attempt to import the PyInstaller splash module.
            # This module only exists when the script is frozen into an EXE.
            import pyi_splash
            error_logs("[create_splash] Splash screen loaded", "info")
        except ImportError:
            # If pyi_splash does not exist (somehow missing), log a warning.
            error_logs("[create_splash] Splash not available", "warning")
    else:
        # Running in normal Python environment (not frozen), log this info.
        error_logs("[create_splash] Running in normal Python, no splash", "warning")
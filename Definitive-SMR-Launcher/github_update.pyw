import __main__
from datetime import date
import requests 
import webbrowser

def github_update():

    today = date.today()
    if str(today) != __main__.gConfigUserInfo["updatelastcheck"]:
        __main__.gConfigUserInfo["updatelastcheck"] = str(today)
        __main__.read_write_config("w")
        __main__.read_write_config("r")
        try:
            GITHUB_API = "https://api.github.com"
            repo = "ageekhere/Definitive-SMR-Launcher"
            response = requests.get(f"{GITHUB_API}/repos/{repo}/releases/latest")
            latest_release = response.json()
            latest_version = latest_release.get("tag_name")

            if latest_version != __main__.gGitHubVersion and latest_version != None:
                __main__.error_logs(f"[github_update] Update found " + str(latest_version), "info")
                # Create a popup window
                popup = __main__.ctk.CTkToplevel(__main__.gApp)
                popup.title("New Update")
                # Define popup dimensions
                popup_width = 300
                popup_height = 100
                # Calculate the screen's width and height
                screen_width = popup.winfo_screenwidth()
                screen_height = popup.winfo_screenheight()
                # Calculate x and y coordinates to center the window
                x = int((screen_width - popup_width) / 2)
                y = int((screen_height - popup_height) / 2)
                popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
                 # Set the popup as a transient window to the root
                popup.transient(__main__.gApp)
                # Ensure all events are directed to the popup (modal behavior)
                popup.grab_set()
                # Focus on the popup window
                popup.focus()
                # Create a button that opens the webpage when clicked
                def open_webpage():
                    # Opens the URL in the default web browser.
                    webbrowser.open("https://github.com/ageekhere/Definitive-SMR-Launcher/releases")
                button = __main__.ctk.CTkButton(popup, text="Download at Github", command=open_webpage)
                button.pack(expand=True, padx=20, pady=20)
            else:
                __main__.error_logs(f"[github_update] UpToDate " + str(latest_version), "info")
        except Exception as e:
            __main__.error_logs(f"[github_update] Cannot Check for updates" + str(e), "error")
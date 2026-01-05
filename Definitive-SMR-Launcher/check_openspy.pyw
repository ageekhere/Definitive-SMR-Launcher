import __main__
import json
import threading
import requests
from datetime import datetime

SERVERS_INDEX_URL = "https://openspy-website.nyc3.digitaloceanspaces.com/servers.json"
#SMRAILROADS_URL = "https://openspy-website.nyc3.digitaloceanspaces.com/servers/smrailroads.json"

CHECK_INTERVAL_SECONDS = 1 * 60  # 5 minutes

def fetch_json(url):
    """Fetch JSON data from a URL and return it as a Python object."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def find_game(servers_index, gamename):
    """Find a game entry by gamename in servers.json (list of dicts)."""
    for game in servers_index:
        if game.get("gamename") == gamename:
            return game
    return None


def timestamp():
    """Return a readable timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def check_smrailroads():
    """Check for smrailroads and get its server data."""
    try:
        servers_index = fetch_json(SERVERS_INDEX_URL)
        sm_game = find_game(servers_index, "smrailroads")

        if not sm_game:
            __main__.error_logs("[check_openspy] There are no active servers", "info")
            __main__.gOnlineServers = 0
            __main__.gPlayersInGame = 0
            __main__.gApp.title("Definitive SMR Launcher - " + str(__main__.gVersion) + 
                " ( Online Servers: " + str(__main__.gOnlineServers) + " Players In Game: " + str(__main__.gPlayersInGame) + " )")
            return

        __main__.gOnlineServers = sm_game['servers']
        __main__.gPlayersInGame = sm_game['players']
        __main__.gApp.title("Definitive SMR Launcher - " + str(__main__.gVersion) + 
            " ( Online Servers: " + str(__main__.gOnlineServers) + " Players In Game: " + str(__main__.gPlayersInGame) + " )")

        __main__.error_logs("[check_openspy] There are " + __main__.gOnlineServers + 
            " servers with " + __main__.gPlayersInGame + " In Game Players", "info")

        #smrailroads_data = fetch_json(SMRAILROADS_URL)
        #print(json.dumps(smrailroads_data, indent=4))

    except requests.RequestException as e:
        __main__.error_logs("[check_openspy] Cannot find servers.jso " + str(e), "warning")

    except Exception as e:
        __main__.error_logs("[check_openspy] Error reading servers.jso " + str(e), "error")

def smrailroads_background_loop(stop_event):
    """Background loop that runs every 5 minutes."""
    while not stop_event.is_set():
        check_smrailroads()
        stop_event.wait(CHECK_INTERVAL_SECONDS)


def check_openspy():
    """
    Start the OpenSpy smrailroads monitor in a background thread.
    Call this ONCE during app startup.
    """
    stop_event = threading.Event()

    thread = threading.Thread(
        target=smrailroads_background_loop,
        args=(stop_event,),
        daemon=True
    )
    thread.start()

    return stop_event
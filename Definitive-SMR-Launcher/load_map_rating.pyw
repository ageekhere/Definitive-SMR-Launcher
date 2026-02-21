import requests
import time
import urllib3
import json
import os
import ast

import __main__
# -----------------------------
# Configuration
# -----------------------------
URL = "https://raw.githubusercontent.com/ageekhere/Definitive-SMR-Launcher/main/map_ratings/map_ratings_list.json"
CACHE_SECONDS = 3600            # 1 hour cache
LOCAL_CACHE_FILE = "map_ratings_cache.json"  # optional disk cache

# Disable SSL warnings (useful if behind a proxy/SSL MITM)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# Internal cache
# -----------------------------

_cached_matrix = None

# -----------------------------
# Loader function
# -----------------------------
def load_map_ratings_matrix(force_refresh=False):
    __main__.error_logs("[load_map_ratings_matrix] Loading cache", "info")

    """
    Returns the map ratings as a matrix:
    [
        [map_ids...],
        [map_names...],
        [urls...],
        [is_stable...],
        [multiplayer...]
    ]
    Downloads JSON from GitHub but caches for 1 hour.
    """
    #global _cached_matrix
    option1_text = __main__.get_config_value("option1")
    option2_text = __main__.get_config_value("option2")

    if option2_text != "" and option2_text !=" ":
        _cached_matrix = ast.literal_eval(option2_text)

    if option1_text == "":
        _last_fetch = 0
    else: 
        _last_fetch = float(option1_text)

    now = time.time()

    # Use in-memory cache if valid
    if option2_text !="" and option2_text !=" ":
        if not force_refresh and _cached_matrix and (now - _last_fetch) < CACHE_SECONDS:
            __main__.error_logs("[load_map_ratings_matrix] Loading map cache", "info")
            return _cached_matrix

    # Try downloading JSON from GitHub
    data = None
    try:
        response = requests.get(URL, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()

        # Save to disk for offline fallback
        with open(LOCAL_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        __main__.error_logs("[load_map_ratings_matrix] Warning: Could not download JSON "+str(e), "error")

        # Try loading from local cache
        if os.path.exists(LOCAL_CACHE_FILE):
            try:
                with open(LOCAL_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    __main__.error_logs("[load_map_ratings_matrix] Loaded map ratings from local cache "+str(e), "info")
            except Exception as e2:
                __main__.error_logs("[load_map_ratings_matrix] Error reading local cache "+str(e2), "error")
                return [[], [], [], [], []]  # nothing available
        else:
            return [[], [], [], [], []]  # nothing available

    # Convert JSON to matrix
    map_ids = []
    map_names = []
    urls = []
    is_stable = []
    multiplayer = []
    try:
        for map_id, info in data.items():
            map_ids.append(map_id)
            map_names.append(info.get("map_name", map_id))  # fallback to ID
            urls.append(info.get("url", ""))
            is_stable.append(info.get("is_stable", ""))    # fallback empty
            multiplayer.append(info.get("multiplayer", ""))  # fallback empty

        _cached_matrix = [map_ids, map_names, urls, is_stable, multiplayer]
        __main__.set_config_value("option2", str(_cached_matrix))
        _last_fetch = now
        __main__.set_config_value("option1", str(_last_fetch))
    except Exception as e:
        __main__.error_logs("[load_map_ratings_matrix] Error reading data"+str(e), "error")        
    return _cached_matrix
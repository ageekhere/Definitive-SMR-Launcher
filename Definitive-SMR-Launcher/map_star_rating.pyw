from bs4 import BeautifulSoup
import re
import json
import os
import __main__

# -----------------------------
# Cache setup
# -----------------------------

CACHE_FILE = "map_ratings_cache.json"

def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

_MAP_RATING_CACHE = _load_cache()

# -----------------------------
# Shared HTTP session
# -----------------------------

if not hasattr(__main__, "http_session"):
    __main__.http_session = __main__.requests.Session()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}

# -----------------------------
# Main function
# -----------------------------

def get_map_rating(url: str):
    """
    Fetch and calculate the rating for a map discussion.
    Results are cached in memory and on disk.
    """

    # Return cached result immediately
    if url in _MAP_RATING_CACHE:
        return _MAP_RATING_CACHE[url]

    full_url = (
        "https://github.com/ageekhere/Definitive-SMR-Launcher/discussions/"
        + url
    )

    try:
        response = __main__.http_session.get(full_url, headers=HEADERS, timeout=10)
    except Exception as e:
        __main__.error_logs(
            f"[get_map_rating] Request error: {e}",
            "error"
        )
        return None

    if response.status_code != 200:
        __main__.error_logs(
            f"[get_map_rating] Failed to fetch page: {response.status_code}",
            "error"
        )
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    full_text = soup.get_text(separator=" ")

    # Extract ratings
    pattern = re.compile(r"(⭐⭐⭐⭐⭐|⭐⭐⭐⭐|⭐⭐⭐|⭐⭐|⭐|Not Working)\s*(\d+%?)")
    matches = pattern.findall(full_text)

    if not matches:
        __main__.error_logs(
            "[get_map_rating] No rating data found. The post format may have changed",
            "warning"
        )
        return None

    option_map = {
        "⭐⭐⭐⭐⭐": {"stars": 5},
        "⭐⭐⭐⭐": {"stars": 4},
        "⭐⭐⭐": {"stars": 3},
        "⭐⭐": {"stars": 2},
        "⭐": {"stars": 1},
        "Not Working": {"stars": 0},
    }

    poll_data = []
    total_percentage = 0
    weighted_sum = 0.0

    for option_code, percent_str in matches:
        percent = int(percent_str.rstrip('%'))
        stars = option_map.get(option_code, {"stars": 0})["stars"]

        poll_data.append(percent_str)
        total_percentage += percent
        weighted_sum += stars * percent

    # Calculate average
    average = weighted_sum / total_percentage if total_percentage > 0 else 0.0

    # Build star display
    full_stars = int(average)
    partial = average - full_stars

    star_display = "⭐" * full_stars
    if partial >= 0.5:
        star_display += "½"

    remaining = 5 - full_stars - (1 if partial >= 0.5 else 0)
    if remaining > 0:
        star_display += "☆" * remaining

    poll_data.append(f"({average:.2f}/5.0)")

    # Extract total votes
    vote_match = re.search(
        r"Not\s*Working\s*0%\D*(\d+)",
        full_text,
        re.IGNORECASE
    )
    total_votes = vote_match.group(1) if vote_match else "Unknown"
    poll_data.append(total_votes)

    # Cache result
    _MAP_RATING_CACHE[url] = poll_data
    _save_cache(_MAP_RATING_CACHE)

    return poll_data

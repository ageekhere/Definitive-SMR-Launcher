from bs4 import BeautifulSoup
import re
import __main__

def get_map_rating(url:str):
    poll_data = []
    url = "https://github.com/ageekhere/Definitive-SMR-Launcher/discussions/" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = __main__.requests.get(url, headers=headers)
    if response.status_code != 200:
        __main__.error_logs("[get_map_rating] Failed to fetch page: " + str(response.status_code), "error")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    full_text = soup.get_text(separator=" ")

    # Extract ratings
    pattern = re.compile(r"(⭐⭐⭐⭐⭐|⭐⭐⭐⭐|⭐⭐⭐|⭐⭐|⭐|Not Working)\s*(\d+%?)")
    matches = pattern.findall(full_text)

    if not matches:
        response.status_code
        __main__.error_logs("[get_map_rating] No rating data found. The post format may have changed ", "warning")
        exit()

    # Mapping for display and calculation
    option_map = {
        "⭐⭐⭐⭐⭐": {"name": "⭐⭐⭐⭐⭐", "stars": 5},
        "⭐⭐⭐⭐": {"name": "⭐⭐⭐⭐", "stars": 4},
        "⭐⭐⭐": {"name": "⭐⭐⭐", "stars": 3},
        "⭐⭐": {"name": "⭐⭐", "stars": 2},
        "⭐": {"name": "⭐", "stars": 1},
        "Not Working": {"name": "Not Working", "stars": 0}
    }

    total_percentage = 0
    weighted_sum = 0.0

    for option_code, percent_str in matches:
        percent = int(percent_str.rstrip('%'))
        info = option_map.get(option_code, {"name": option_code, "stars": 0})
        poll_data.append(percent_str)
        
        total_percentage += percent
        weighted_sum += info['stars'] * percent

    # Calculate average
    if total_percentage > 0:
        average = weighted_sum / total_percentage
    else:
        average = 0.0

    # Display average as stars
    full_stars = int(average)
    partial = average - full_stars
    star_display = "⭐" * full_stars
    if partial >= 0.5:
        star_display += "½"  # Optional half-star if close
    elif partial > 0:
        star_display += ""  # No partial for simplicity

    if full_stars < 5:
        star_display += "☆" * (5 - full_stars - (1 if partial >= 0.5 else 0))

    poll_data.append(f"({average:.2f}/5.0)")

    # Extract total votes (the standalone number after the table, e.g., "1")
    vote_match = re.search(r"Not\s*Working\s*0%\D*(\d+)", full_text, re.IGNORECASE)
    total_votes = vote_match.group(1) if vote_match else "Unknown"

    poll_data.append(f"{total_votes}")
    return poll_data
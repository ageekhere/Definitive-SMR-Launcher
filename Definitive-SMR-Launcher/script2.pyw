import requests
from bs4 import BeautifulSoup
import re

url = "https://github.com/ageekhere/Definitive-SMR-Launcher/discussions/3"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"Failed to fetch page: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")
full_text = soup.get_text(separator=" ")

# Extract ratings
pattern = re.compile(r"(⭐⭐⭐⭐⭐|⭐⭐⭐⭐|⭐⭐⭐|⭐⭐|⭐|Not Working)\s*(\d+%?)")
matches = pattern.findall(full_text)

if not matches:
    print("No rating data found. The post format may have changed.")
    exit()

print("Rating Results (manually updated by author):\n")

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
    print(f"{info['name']}: {percent_str}")
    
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

print(f"\nAverage Rating: {star_display} ({average:.2f}/5.0)")

# Extract total votes (the standalone number after the table, e.g., "1")
vote_match = re.search(r"Not\s*Working\s*0%\D*(\d+)", full_text, re.IGNORECASE)
total_votes = vote_match.group(1) if vote_match else "Unknown"

print(f"Total Votes: {total_votes}")
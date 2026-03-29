import os
import requests
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_BASE_URL = "https://api.the-odds-api.com/v4"

def debug_fetch_odds():
    url = f"{ODDS_BASE_URL}/sports/baseball_mlb/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "american"
    }
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total Games Found: {len(data)}")
        if len(data) > 0:
            print("Sample Game Data:")
            print(data[0])
    else:
        print(f"Error Response: {response.text}")

if __name__ == "__main__":
    debug_fetch_odds()

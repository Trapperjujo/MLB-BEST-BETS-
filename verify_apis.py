import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api(name, url, headers, params):
    print(f"--- Testing {name} ---")
    try:
        r = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.json().get('message', 'SUCCESS (Data Payload Received)')}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

# Institutional Keys
key = os.getenv("API_SPORTS_KEY")
host_matrix = "baseball4.p.rapidapi.com"
host_live = "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"

# 1. Test baseball4 (Matrix)
test_api(
    "baseball4 (Statcast Matrix)",
    "https://baseball4.p.rapidapi.com/v1/mlb/games-matrix",
    {"x-rapidapi-key": key, "x-rapidapi-host": host_matrix},
    {"gamePk": "633282"}
)

# 2. Test tank01 (Live Scores)
test_api(
    "tank01 (Live Scores & Top Performers)",
    "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBScoresOnly",
    {"x-rapidapi-key": key, "x-rapidapi-host": host_live},
    {"gameDate": "20260415"}
)

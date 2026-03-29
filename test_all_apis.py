import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def test_odds_api():
    print("--- [1] Testing THE ODDS API ---")
    key = os.getenv("ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={key}&regions=us&markets=h2h"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Success: Found {len(data)} games.")
        else:
            print(f"[ERROR] Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")

def test_balldontlie_api():
    print("\n--- [2] Testing BALLDONTLIE API ---")
    key = os.getenv("BALLDONTLIE_API_KEY")
    url = "https://api.balldontlie.io/v1/mlb/games"
    headers = {"Authorization": key}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", [])
            print(f"[OK] Success: Found {len(data)} recent games.")
        else:
            print(f"[ERROR] Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")

def test_api_sports():
    print("\n--- [3] Testing API-SPORTS (MLB) ---")
    key = os.getenv("API_SPORTS_KEY")
    url = "https://v1.baseball.api-sports.io/games?league=1&season=2026"
    headers = {"x-rapidapi-key": key, "x-rapidapi-host": "v1.baseball.api-sports.io"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("response", [])
            print(f"[OK] Success: Found {len(data)} games for 2026.")
        else:
            print(f"[ERROR] Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")

def test_mlb_stats_api():
    print("\n--- [4] Testing MLB STATS API (Public) ---")
    url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"[OK] Success: Public API is reachable.")
        else:
            print(f"[ERROR] Failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")

if __name__ == "__main__":
    print(f"=== COMPREHENSIVE API DIAGNOSTIC (System Time: {datetime.now()}) ===\n")
    test_odds_api()
    test_balldontlie_api()
    test_api_sports()
    test_mlb_stats_api()
    print("\n=== DIAGNOSTIC COMPLETE ===")

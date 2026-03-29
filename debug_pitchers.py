import requests
import json
from datetime import datetime

def test_mlb_stats_api(date=None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=probablePitcher&date={date}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Games Found for {date}: {data.get('totalGames', 0)}")
        for date_info in data.get('dates', []):
            for game in date_info.get('games', []):
                h_team = game['teams']['home']['team']['name']
                a_team = game['teams']['away']['team']['name']
                h_pitcher = game['teams']['home'].get('probablePitcher', {}).get('fullName', 'TBA')
                a_pitcher = game['teams']['away'].get('probablePitcher', {}).get('fullName', 'TBA')
                print(f"{a_team} @ {h_team} | Starters: {a_pitcher} vs {h_pitcher}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    # Test for March 29, 2026 (System today)
    print("--- TESTING FOR TODAY (System 2026-03-29) ---")
    test_mlb_stats_api("2026-03-29")
    print("\n--- TESTING FOR TOMORROW (2026-03-30) ---")
    test_mlb_stats_api("2026-03-30")

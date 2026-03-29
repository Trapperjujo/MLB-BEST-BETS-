import requests
import json
from datetime import datetime, timedelta

def get_mlb_schedule(date_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        games = []
        for date_info in data.get("dates", []):
            for game in date_info.get("games", []):
                games.append({
                    "id": game.get("gamePk"),
                    "away_team": game.get("teams", {}).get("away", {}).get("team", {}).get("name"),
                    "home_team": game.get("teams", {}).get("home", {}).get("team", {}).get("name"),
                    "time": game.get("gameDate")
                })
        return games
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

if __name__ == "__main__":
    today = "2026-03-29"
    tomorrow = "2026-03-30"
    
    print(f"--- Schedule for {today} ---")
    today_games = get_mlb_schedule(today)
    for g in today_games:
        print(f"{g['away_team']} @ {g['home_team']} (ID: {g['id']})")
    
    print(f"\n--- Schedule for {tomorrow} ---")
    tomorrow_games = get_mlb_schedule(tomorrow)
    for g in tomorrow_games:
        print(f"{g['away_team']} @ {g['home_team']} (ID: {g['id']})")

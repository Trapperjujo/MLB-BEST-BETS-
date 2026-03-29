import requests
import pandas as pd
from datetime import datetime
import os
import time

def fetch_season_games(year):
    print(f"Fetching games for {year} season...")
    start_date = f"{year}-03-20"
    end_date = f"{year}-10-30"
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_date}&endDate={end_date}&hydrate=team,probablePitcher"
    
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        games_list = []
        for date_info in data.get("dates", []):
            for game in date_info.get("games", []):
                games_list.append({
                    "game_id": game.get("gamePk"),
                    "date": game.get("gameDate")[:10],
                    "home_team": game.get("teams", {}).get("home", {}).get("team", {}).get("name"),
                    "away_team": game.get("teams", {}).get("away", {}).get("team", {}).get("name"),
                    "home_score": game.get("teams", {}).get("home", {}).get("score", 0),
                    "away_score": game.get("teams", {}).get("away", {}).get("score", 0),
                    "status": game.get("status", {}).get("abstractGameState"),
                    "home_pitcher": game.get("teams", {}).get("home", {}).get("probablePitcher", {}).get("fullName", "TBD"),
                    "away_pitcher": game.get("teams", {}).get("away", {}).get("probablePitcher", {}).get("fullName", "TBD")
                })
        return games_list
    except Exception as e:
        print(f"Error fetching {year}: {e}")
        return []

def main():
    os.makedirs("data/raw", exist_ok=True)
    all_games = []
    
    for year in [2024, 2025, 2026]:
        games = fetch_season_games(year)
        all_games.extend(games)
        print(f"Success: Found {len(games)} games for {year}")
        time.sleep(1) # Be nice to API

    df = pd.DataFrame(all_games)
    output_path = "data/raw/master_history_2024_2026.csv"
    df.to_csv(output_path, index=False)
    print(f"\nDATABASE UPDATED: {len(df)} games saved to {output_path}")

if __name__ == "__main__":
    main()

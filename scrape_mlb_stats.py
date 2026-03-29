import requests
import pandas as pd
import os
import json
from datetime import datetime, timedelta

def scrape_mlb_season(year):
    print(f"Scraping MLB.com Official Stats API for {year}...")
    start_date = datetime(year, 3, 20)
    end_date = datetime(year, 10, 5)
    
    all_games = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            if "dates" in data and len(data["dates"]) > 0:
                for game in data["dates"][0]["games"]:
                    all_games.append({
                        "game_id": game.get("gamePk"),
                        "date": date_str,
                        "home_team": game["teams"]["home"]["team"]["name"],
                        "away_team": game["teams"]["away"]["team"]["name"],
                        "home_score": game["teams"]["home"].get("score", 0),
                        "away_score": game["teams"]["away"].get("score", 0),
                        "status": game["status"]["abstractGameState"]
                    })
            print(f"  Processed {date_str} - Games found: {len(data.get('dates', [{}])[0].get('games', [])) if 'dates' in data and len(data['dates']) > 0 else 0}")
        except Exception as e:
            print(f"  Error on {date_str}: {e}")
            
        current_date += timedelta(days=1)
    
    df = pd.DataFrame(all_games)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(f"data/raw/mlb_official_{year}.csv", index=False)
    print(f"Saved {len(df)} games to data/raw/mlb_official_{year}.csv")
    return df

if __name__ == "__main__":
    scrape_mlb_season(2024)

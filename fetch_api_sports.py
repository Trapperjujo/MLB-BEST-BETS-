import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_api_sports_games(season, league_id=1):
    api_key = os.getenv("API_SPORTS_KEY")
    url = f"https://v1.baseball.api-sports.io/games?league={league_id}&season={season}"
    headers = {
        'x-rapidapi-host': 'v1.baseball.api-sports.io',
        'x-rapidapi-key': api_key
    }
    
    print(f"Fetching API-Sports data for {season}...")
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get("errors"):
            print(f"API Errors: {data['errors']}")
            return None
            
        games = []
        for g in data.get("response", []):
            games.append({
                "game_id": g.get("id"),
                "date": g.get("date"),
                "home_team": g["teams"]["home"]["name"],
                "away_team": g["teams"]["away"]["name"],
                "home_score": g["scores"]["home"]["total"],
                "away_score": g["scores"]["away"]["total"],
                "status": g["status"]["long"]
            })
            
        df = pd.DataFrame(games)
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv(f"data/raw/api_sports_{season}.csv", index=False)
        print(f"Saved {len(df)} games to data/raw/api_sports_{season}.csv")
        return df
    except Exception as e:
        print(f"Error fetching API-Sports data: {e}")
        return None

if __name__ == "__main__":
    fetch_api_sports_games(2024)
    fetch_api_sports_games(2025)

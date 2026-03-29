import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY")

ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
BDL_BASE_URL = "https://api.balldontlie.io/v1/mlb"
SPORTS_BASE_URL = "https://v1.baseball.api-sports.io"

def get_mlb_odds(regions="us,uk,eu,au", markets="h2h"):
    """Fetches real-time MLB odds from The Odds API across multiple regions."""
    url = f"{ODDS_BASE_URL}/sports/baseball_mlb/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "american"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching odds: {response.status_code}")
        return []

def get_mlb_schedule(date_str):
    """Fetches official MLB schedule and probable pitchers from Stats API."""
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        games = []
        for date_info in data.get("dates", []):
            for game in date_info.get("games", []):
                games.append({
                    "game_id": game.get("gamePk"),
                    "home_team": game.get("teams", {}).get("home", {}).get("team", {}).get("name"),
                    "away_team": game.get("teams", {}).get("away", {}).get("team", {}).get("name"),
                    "commence_time": game.get("gameDate"),
                    "home_pitcher": game.get("teams", {}).get("home", {}).get("probablePitcher", {}).get("fullName", "TBD"),
                    "away_pitcher": game.get("teams", {}).get("away", {}).get("probablePitcher", {}).get("fullName", "TBD"),
                    "status": game.get("status", {}).get("abstractGameState")
                })
        return games
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

def get_mlb_games(date=None):
    """Fetches MLB games from balldontlie."""
    url = f"{BDL_BASE_URL}/games"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    params = {}
    if date:
        params["dates[]"] = date
        
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error fetching games: {response.status_code}")
        return []

def get_player_stats(player_id, season=2026):
    """Fetches player season stats from balldontlie."""
    url = f"{BDL_BASE_URL}/season_stats"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    params = {
        "season": season,
        "player_ids[]": player_id
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error fetching player stats: {response.status_code}")
        return []

def get_team_standings(season=2026):
    """Fetches team standings from balldontlie."""
    url = f"{BDL_BASE_URL}/standings"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    params = {"season": season}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Error fetching standings: {response.status_code}")
        return []

def get_api_sports_games(date=None):
    """Fetches MLB games from API-Sports."""
    url = f"{SPORTS_BASE_URL}/games"
    headers = {
        "x-rapidapi-key": API_SPORTS_KEY,
        "x-rapidapi-host": "v1.baseball.api-sports.io"
    }
    params = {"league": "1", "season": "2026"} # MLB is usually league 1
    if date:
        params["date"] = date
        
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print(f"Error fetching API-Sports games: {response.status_code}")
        return []

def process_odds_data(odds_json):
    """Processes raw Odds API JSON into a flat DataFrame."""
    processed_data = []
    for game in odds_json:
        home_team = game.get("home_team")
        away_team = game.get("away_team")
        commence_time = game.get("commence_time")
        
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    processed_data.append({
                        "game_id": game.get("id"),
                        "home_team": home_team,
                        "away_team": away_team,
                        "commence_time": commence_time,
                        "bookmaker": bookmaker.get("title"),
                        "market": market.get("key"),
                        "outcome": outcome.get("name"),
                        "odds": outcome.get("price")
                    })
    return pd.DataFrame(processed_data)

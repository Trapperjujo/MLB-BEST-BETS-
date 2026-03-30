import os
import requests
import pandas as pd
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from core.config import CURRENT_SEASON

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY")

ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
BDL_BASE_URL = "https://api.balldontlie.io/v1/mlb"
SPORTS_BASE_URL = "https://v1.baseball.api-sports.io"

def get_mlb_odds(regions: str = "us,uk,eu,au", markets: str = "h2h") -> List[Dict[str, Any]]:
    """Fetches real-time MLB odds from The Odds API across multiple regions."""
    url = f"{ODDS_BASE_URL}/sports/baseball_mlb/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "american"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return []

def get_mlb_schedule(date_str: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches official MLB schedule and probable pitchers from Stats API for a date or range."""
    if start_date and end_date:
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_date}&endDate={end_date}&hydrate=probablePitcher"
    else:
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
    
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        games = []
        for date_info in data.get("dates", []):
            game_date = date_info.get("date")
            for game in date_info.get("games", []):
                games.append({
                    "gamePk": game.get("gamePk"),
                    "game_id": f"{game_date}_{game.get('gamePk')}",
                    "home_team": game.get("teams", {}).get("home", {}).get("team", {}).get("name"),
                    "away_team": game.get("teams", {}).get("away", {}).get("team", {}).get("name"),
                    "commence_time": game.get("gameDate"),
                    "game_day": game_date,
                    "home_pitcher": game.get("teams", {}).get("home", {}).get("probablePitcher", {}).get("fullName", "TBD"),
                    "away_pitcher": game.get("teams", {}).get("away", {}).get("probablePitcher", {}).get("fullName", "TBD"),
                    "status": game.get("status", {}).get("abstractGameState")
                })
        return games
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

def get_mlb_games(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches MLB games from balldontlie."""
    url = f"{BDL_BASE_URL}/games"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    params = {}
    if date:
        params["dates[]"] = date
        
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching BDL games: {e}")
        return []

def get_player_stats(player_id: int, season: int = CURRENT_SEASON) -> List[Dict[str, Any]]:
    """Fetches player season stats from balldontlie."""
    url = f"{BDL_BASE_URL}/season_stats"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    params = {
        "season": season,
        "player_ids[]": player_id
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching player stats: {e}")
        return []

def get_team_standings(season: int = CURRENT_SEASON) -> List[Dict[str, Any]]:
    """Fetches team standings from balldontlie."""
    url = f"{BDL_BASE_URL}/standings"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    params = {"season": season}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"Error fetching standings: {e}")
        return []

def get_api_sports_games(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches MLB games from API-Sports."""
    url = f"{SPORTS_BASE_URL}/games"
    headers = {
        "x-rapidapi-key": API_SPORTS_KEY,
        "x-rapidapi-host": "v1.baseball.api-sports.io"
    }
    params = {"league": "1", "season": str(CURRENT_SEASON)}
    if date:
        params["date"] = date
        
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("response", [])
    except Exception as e:
        print(f"Error fetching API-Sports games: {e}")
        return []

def get_game_matrix(gamePk: int) -> Dict[str, Any]:
    """Fetches high-fidelity matchup matrix (Statcast) from baseball4.p.rapidapi.com."""
    url = "https://baseball4.p.rapidapi.com/v1/mlb/games-matrix"
    headers = {
        "x-rapidapi-key": os.getenv("API_SPORTS_KEY"), # RapidAPI credential shared via .env
        "x-rapidapi-host": "baseball4.p.rapidapi.com"
    }
    params = {"gamePk": str(gamePk)}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json() # Return JSON directly to allow UI-level error handling
    except Exception as e:
        print(f"Error fetching game matrix: {e}")
        return {}

def get_tank01_scores(game_date: str) -> dict:
    """
    Fetches live scores and top performers from tank01 API.
    game_date: YYYYMMDD
    """
    url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBScoresOnly"
    headers = {
        "x-rapidapi-key": os.getenv("API_SPORTS_KEY"),
        "x-rapidapi-host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"
    }
    params = {"gameDate": game_date, "topPerformers": "true"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print(f"Error fetching live scores: {e}")
        return {}

def process_odds_data(odds_json: List[Dict[str, Any]]) -> pd.DataFrame:
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

import os
import requests
import pandas as pd
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from core.config import CURRENT_SEASON
from core.logger import terminal_logger as logger

load_dotenv()

BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY") # Shared RapidAPI Key

BDL_BASE_URL = "https://api.balldontlie.io/v1/mlb"
SPORTS_BASE_URL = "https://v1.baseball.api-sports.io"
TANK01_BASE_URL = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"

def get_rapid_odds(game_date: str) -> Dict[str, Any]:
    """
    Fetches MLB odds using a fallback chain: Tank01 (Primary) -> API-Sports (Secondary).
    game_date: YYYYMMDD
    """
    # 1. Primary: Tank01
    url_t1 = f"{TANK01_BASE_URL}/getMLBBettingOdds"
    headers_t1 = {
        "x-rapidapi-key": API_SPORTS_KEY,
        "x-rapidapi-host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"
    }
    params_t1 = {"gameDate": game_date}
    
    try:
        logger.info(f"RapidAPI: Attempting Tank01 Odds Fetch for {game_date}")
        resp = requests.get(url_t1, headers=headers_t1, params=params_t1)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("body") and len(data["body"]) > 0:
                logger.info("RapidAPI: Tank01 Odds Success (Primary)")
                return {"source": "tank01", "data": data["body"]}
    except Exception as e:
        logger.warning(f"RapidAPI: Tank01 Odds Failed, falling back: {e}")

    # 2. Fallback: API-Sports
    url_as = f"{SPORTS_BASE_URL}/odds"
    headers_as = {
        "x-rapidapi-key": API_SPORTS_KEY,
        "x-rapidapi-host": "v1.baseball.api-sports.io"
    }
    # API-Sports expects date format YYYY-MM-DD
    as_date = f"{game_date[:4]}-{game_date[4:6]}-{game_date[6:]}"
    params_as = {"league": "1", "season": "2026", "date": as_date}
    
    try:
        logger.info(f"RapidAPI: Attempting API-Sports Fallback for {as_date}")
        resp = requests.get(url_as, headers=headers_as, params=params_as)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("response") and len(data["response"]) > 0:
                logger.info("RapidAPI: API-Sports Fallback Success")
                return {"source": "api-sports", "data": data["response"]}
    except Exception as e:
        logger.error(f"RapidAPI: Critical Fallback Failure: {e}")
        
    return {"source": None, "data": []}

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
        logger.error(f"Error fetching schedule: {e}")
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
        logger.error(f"Error fetching BDL games: {e}")
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
        logger.error(f"Error fetching player stats: {e}")
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
        logger.error(f"Error fetching standings: {e}")
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
        logger.error(f"Error fetching API-Sports games: {e}")
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
        logger.error(f"Error fetching game matrix: {e}")
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
        logger.error(f"Error fetching live scores: {e}")
        return {}

def process_rapid_odds(odds_payload: Dict[str, Any]) -> pd.DataFrame:
    """Processes either Tank01 or API-Sports JSON into a flat dashboard-ready DataFrame."""
    source = odds_payload.get("source")
    data = odds_payload.get("data", [])
    processed = []
    
    if source == "tank01":
        # Tank01 format: { gameID: { "playerProps": ..., "gameOdds": { "ml": {...} } } }
        for g_id, g_data in data.items():
            odds_dict = g_data.get("gameOdds", {})
            for market_key, market_data in odds_dict.items():
                if market_key == "ml": # Moneyline (h2h)
                    # Tank01 format: "ml": { "home": "-150", "away": "+130" }
                    # We need to extract teams from the g_id (e.g. "MIN@SEA_20260330")
                    try:
                        teams_part = g_id.split("_")[0]
                        away_abbr, home_abbr = teams_part.split("@")
                        # We use ABBR_MAP from elo_ratings elsewhere, but here we just need to match outcomes.
                        # For consistency with app.py merging, we store the abbr or full name.
                        from core.elo_ratings import ABBR_MAP
                        home_team = ABBR_MAP.get(home_abbr, home_abbr)
                        away_team = ABBR_MAP.get(away_abbr, away_abbr)
                        
                        processed.append({
                            "game_id": g_id,
                            "home_team": home_team,
                            "away_team": away_team,
                            "bookmaker": "🛰️ Institutional Tank01 Feed",
                            "market": "h2h",
                            "outcome": home_team,
                            "odds": int(market_data.get("home", 0))
                        })
                        processed.append({
                            "game_id": g_id,
                            "home_team": home_team,
                            "away_team": away_team,
                            "bookmaker": "🛰️ Institutional Tank01 Feed",
                            "market": "h2h",
                            "outcome": away_team,
                            "odds": int(market_data.get("away", 0))
                        })
                    except: continue

    elif source == "api-sports":
        # API-Sports format: list of objects with "game", "league", "bookmakers"
        for item in data:
            g_info = item.get("game", {})
            h_team = item.get("teams", {}).get("home", {}).get("name")
            a_team = item.get("teams", {}).get("away", {}).get("name")
            
            for bm in item.get("bookmakers", []):
                for market in bm.get("bets", []):
                    if market.get("name") in ["Moneyline", "Home/Away"]:
                        for val in market.get("values", []):
                            processed.append({
                                "game_id": str(g_info.get("id")),
                                "home_team": h_team,
                                "away_team": a_team,
                                "bookmaker": bm.get("name"),
                                "market": "h2h",
                                "outcome": val.get("value"), # Usually "Home" or "Away" or team name
                                "odds": val.get("odd") # Usually decimal, but we'll adapt if needed
                            })
                            
    return pd.DataFrame(processed)

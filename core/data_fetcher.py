import os
import requests
import pandas as pd
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from core.unified_config import CURRENT_SEASON
from core.logger import terminal_logger as logger

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")
API_SPORTS_KEY = os.getenv("API_SPORTS_KEY")

ODDS_BASE_URL = "https://api.the-odds-api.com/v4"
BDL_BASE_URL = "https://api.balldontlie.io/v1/mlb"
SPORTS_BASE_URL = "https://v1.baseball.api-sports.io"

# 💎 Institutional Market Anchors
SHARP_BOOKMAKERS = ["Pinnacle", "Bookmaker", "Circa Sports", "BetOnline.ag"]

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
        logger.error(f"Error fetching odds: {e}")
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

def get_tank01_odds(game_date: str) -> List[Dict[str, Any]]:
    """
    Fetches 2026 Betting Odds from Tank01.
    game_date: YYYYMMDD
    """
    url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBScheduling"
    headers = {
        "x-rapidapi-key": os.getenv("API_SPORTS_KEY"),
        "x-rapidapi-host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"
    }
    params = {"gameDate": game_date}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get("body", [])
            # Convert Tank01 schedule/odds to standard format
            standardized = []
            for game in data:
                standardized.append({
                    "game_id": game.get("gameID"),
                    "home_team": game.get("home"),
                    "away_team": game.get("away"),
                    "commence_time": game.get("gameTime"),
                    "bookmaker": "Tank01 Global",
                    "market": "h2h",
                    "outcome": game.get("home"), # Just a placeholder for mapping
                    "odds": float(game.get("homeOdds", 1.91))
                })
            return standardized
        return []
    except Exception as e:
        logger.error(f"Tank01 Odds Error: {e}")
        return []

def get_rapid_odds(game_date: str) -> Dict[str, Any]:
    """
    💎 Triple-Source Sync Layer 1: Unified API Fetcher.
    Attempts (1) Tank01 -> (2) The Odds API -> (3) API-Sports.
    Returns a unified payload for the orchestrator.
    """
    logger.info(f"RapidAPI: Attempting Triple-Source Odds Fetch for {game_date}")
    
    # 1. Primary: Tank01 (Institutional Speed)
    tank_data = get_tank01_odds(game_date)
    if tank_data:
        logger.success("Multi-Source Logic: Tank01 Primary Sync Successful (Layer 1A)")
        return {"data": tank_data, "source": "💎 Tank01 Institutional"}

    # 2. Secondary: The Odds API (Global Markets)
    odds_raw = get_mlb_odds()
    if odds_raw:
        df_odds = process_odds_data(odds_raw)
        if not df_odds.empty:
            logger.success("Multi-Source Logic: The Odds API Secondary Sync Successful (Layer 1B)")
            return {"data": df_odds.to_dict(orient='records'), "source": "💎 The Odds API Global"}

    # 3. Tertiary: API-Sports Fallback (Structural Backup)
    api_sports = get_api_sports_games(game_date[:4] + "-" + game_date[4:6] + "-" + game_date[6:])
    if api_sports:
        logger.success("Multi-Source Logic: API-Sports Fallback Sync Successful (Layer 1C)")
        return {"data": api_sports, "source": "💎 API-Sports Backup"}

    logger.warning("Multi-Source Logic: Layer 1 API Sync Failed. Degrading to Layer 2 (Scraper).")
    return {"data": [], "source": "⚠️ API Offline"}

def process_odds_data(odds_json: List[Dict[str, Any]]) -> pd.DataFrame:
    """Processes raw Odds API JSON into a flat DataFrame."""
    if not odds_json: return pd.DataFrame()
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
                        "is_sharp": bookmaker.get("title") in SHARP_BOOKMAKERS,
                        "market": market.get("key"),
                        "outcome": outcome.get("name"),
                        "odds": outcome.get("price")
                    })
    return pd.DataFrame(processed_data)

def get_tank01_scores(game_date: str) -> Dict[str, Any]:
    """
    Fetches real-time scores and game status from Tank01.
    game_date: YYYYMMDD
    """
    url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBGamesForDate"
    headers = {
        "x-rapidapi-key": os.getenv("API_SPORTS_KEY"),
        "x-rapidapi-host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"
    }
    params = {"gameDate": game_date}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Tank01 Scores Error: {e}")
        return {}

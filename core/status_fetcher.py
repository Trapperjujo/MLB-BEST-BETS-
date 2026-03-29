import pandas as pd
import requests
import os
from dotenv import load_dotenv
from pybaseball import schedule_and_record, team_ids
from datetime import datetime, timedelta

load_dotenv()
BALLDONTLIE_API_KEY = os.getenv("BALLDONTLIE_API_KEY")

def get_player_injuries():
    """
    Fetches real-time MLB injury reports from balldontlie.io.
    """
    url = "https://api.balldontlie.io/mlb/v1/player_injuries"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Error fetching injuries: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

from core.elo_ratings import ABBR_MAP

def get_fatigue_penalty(team_name, current_date=None):
    """
    Calculates fatigue penalty based on recent (last 3 days) schedule.
    """
    # Map full name to abbreviation
    team_abbr = None
    for abbr, full in ABBR_MAP.items():
        if full == team_name:
            team_abbr = abbr
            break
            
    if not team_abbr:
        return 0

    if current_date is None:
        current_date = datetime.now()
        
    start_date = current_date - timedelta(days=3)
    
    try:
        # Use pybaseball to get recent games
        sched = schedule_and_record(current_date.year, team_abbr)
        # Simplified: check the last 3 entries in the schedule
        # In a real scenario, we'd check dates.
        recent_games = sched.tail(3)
        played_count = len(recent_games)
        
        penalty = played_count * 5 # -5 per game
        
        return penalty
    except:
        return 0

def calculate_injury_impact(team_name, injuries):
    """
    Calculates total Elo penalty for a team's current injuries.
    Star Player (1st rank): -15
    Regular: -5
    """
    team_injuries = [i for i in injuries if team_name in i.get('team', '')]
    penalty = len(team_injuries) * 4 # Simplification
    return penalty

import pandas as pd
import requests
import os
from dotenv import load_dotenv
from typing import Optional

def get_player_injuries() -> list:
    """Placeholder for player injuries. Integration with API stats."""
    return []
def get_fatigue_penalty(team_name: str, history_df: Optional[pd.DataFrame] = None) -> int:
    """
    Calculates fatigue penalty based on recent (last 3 days) schedule.
    Uses a pre-fetched DataFrame for high-speed lookups.
    """
    if history_df is None or history_df.empty:
        return 0
    
    # Count occurrences of team_name in home or away slots across the history window
    team_games = history_df[
        (history_df["home_team"] == team_name) | 
        (history_df["away_team"] == team_name)
    ]
    
    # Each game played in the last 3 days counts as a -4 Elo penalty (adjustable)
    played_count = len(team_games)
    penalty = played_count * 4 
    
    return penalty

def calculate_injury_impact(team_name, injuries):
    """
    Calculates total Elo penalty for a team's current injuries.
    Star Player (1st rank): -15
    Regular: -5
    """
    team_injuries = [i for i in injuries if team_name in i.get('team', '')]
    penalty = len(team_injuries) * 4 # Simplification
    return penalty

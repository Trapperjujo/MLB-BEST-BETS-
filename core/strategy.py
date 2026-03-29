import pandas as pd
import datetime
from core.elo_ratings import normalize_team_name

# MLB Divisions mapping
MLB_DIVISIONS = {
    "AL East": ["Baltimore Orioles", "Boston Red Sox", "New York Yankees", "Tampa Bay Rays", "Toronto Blue Jays"],
    "AL Central": ["Chicago White Sox", "Cleveland Guardians", "Detroit Tigers", "Kansas City Royals", "Minnesota Twins"],
    "AL West": ["Houston Astros", "Los Angeles Angels", "Oakland Athletics", "Seattle Mariners", "Texas Rangers"],
    "NL East": ["Atlanta Braves", "Miami Marlins", "New York Mets", "Philadelphia Phillies", "Washington Nationals"],
    "NL Central": ["Chicago Cubs", "Cincinnati Reds", "Milwaukee Brewers", "Pittsburgh Pirates", "St. Louis Cardinals"],
    "NL West": ["Arizona Diamondbacks", "Colorado Rockies", "Los Angeles Dodgers", "San Diego Padres", "San Francisco Giants"]
}

def is_divisional_matchup(home_team: str, away_team: str) -> bool:
    """Checks if a matchup is within the same division, after normalization."""
    h = normalize_team_name(home_team)
    a = normalize_team_name(away_team)
    for division, teams in MLB_DIVISIONS.items():
        if h in teams and a in teams:
            return True
    return False

def get_bullpen_fatigue(team_id, last_3_days_data):
    """
    Analyzes bullpen usage over the last 3 days. 
    (Placeholder: This would count innings pitched by key relievers).
    """
    # Simple heuristic: If multiple key relievers pitched > 20 balls or in consecutive days
    # Return a fatigue score (0.0 to 1.0)
    return 0.2 # Placeholder

def calculate_weather_factor(temp, wind_speed, wind_direction, park):
    """
    Calculates a scoring multiplier based on weather and park.
    (Placeholder: Based on Action Network findings).
    """
    # Over: Wind blowing out at Wrigley Field (> 10mph)
    # Under: Wind blowing in at 5+ MPH
    # Temp: Cold weather suppresses scoring
    factor = 1.0
    if wind_speed > 5 and wind_direction == "in":
        factor *= 0.95
    elif wind_speed > 10 and wind_direction == "out":
        factor *= 1.05
    return factor

def detect_reverse_line_movement(opening_odds, current_odds, public_percentage):
    """
    Detects RLM: Line moving against public betting.
    (e.g., Team A get 80% bets but line moves from -150 to -130).
    """
    # Calculate implied change
    pass # Placeholder

def strategy_scorer(matchup_data, model_prob, market_odds):
    """
    Scores a bet based on the combination of EV and situational strategies.
    (Divisional Underdog, F5, Bullpen stress, etc.)
    """
    score = 0
    # +1 for Divisional Underdog
    if matchup_data["is_underdog"] and matchup_data.get("is_divisional", False):
        score += 1
        
    # +1 for F5 (First 5 innings) focus
    if matchup_data.get("strategy_type") == "F5":
        score += 1

    return score

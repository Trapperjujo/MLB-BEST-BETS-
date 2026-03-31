import json
import os

from core.unified_config import MLB_HFA

# 2026 MLB Opening Day Elo Ratings (Baseline)
# Calibrated for March 29, 2026 based on 2025 seasonal performance.
# League Average is 1500.

ELO_BASES = {
    "Toronto Blue Jays": 1505,
    "New York Yankees": 1555,
    "Baltimore Orioles": 1565,
    "Tampa Bay Rays": 1515,
    "Boston Red Sox": 1495,
    "Houston Astros": 1545,
    "Los Angeles Dodgers": 1595,
    "Atlanta Braves": 1575,
    "Philadelphia Phillies": 1550,
    "New York Mets": 1500,
    "Miami Marlins": 1460,
    "Washington Nationals": 1440,
    "Cleveland Guardians": 1520,
    "Minnesota Twins": 1510,
    "Detroit Tigers": 1480,
    "Kansas City Royals": 1475,
    "Chicago White Sox": 1410,
    "Texas Rangers": 1525,
    "Seattle Mariners": 1515,
    "Los Angeles Angels": 1465,
    "Oakland Athletics": 1430,
    "Milwaukee Brewers": 1510,
    "Chicago Cubs": 1505,
    "Cincinnati Reds": 1490,
    "St. Louis Cardinals": 1495,
    "Pittsburgh Pirates": 1470,
    "San Diego Padres": 1530,
    "Arizona Diamondbacks": 1525,
    "San Francisco Giants": 1500,
    "Colorado Rockies": 1420
}

# Mapping for abbreviations to full names (standardized)
ABBR_MAP = {
    'TOR': 'Toronto Blue Jays',
    'NYY': 'New York Yankees',
    'BAL': 'Baltimore Orioles',
    'TBR': 'Tampa Bay Rays',
    'BOS': 'Boston Red Sox',
    'HOU': 'Houston Astros',
    'LAD': 'Los Angeles Dodgers',
    'ATL': 'Atlanta Braves',
    'PHI': 'Philadelphia Phillies',
    'NYM': 'New York Mets',
    'MIA': 'Miami Marlins',
    'WSN': 'Washington Nationals',
    'CLE': 'Cleveland Guardians',
    'MIN': 'Minnesota Twins',
    'DET': 'Detroit Tigers',
    'KCR': 'Kansas City Royals',
    'CHW': 'Chicago White Sox',
    'TEX': 'Texas Rangers',
    'SEA': 'Seattle Mariners',
    'LAA': 'Los Angeles Angels',
    'OAK': 'Oakland Athletics',
    'ATH': 'Oakland Athletics', # Common alias in Odds API/Stats API
    'MIL': 'Milwaukee Brewers',
    'CHC': 'Chicago Cubs',
    'CIN': 'Cincinnati Reds',
    'STL': 'St. Louis Cardinals',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',
    'SD': 'San Diego Padres',
    'ARI': 'Arizona Diamondbacks',
    'AZ': 'Arizona Diamondbacks',
    'SFG': 'San Francisco Giants',
    'SF': 'San Francisco Giants',
    'COL': 'Colorado Rockies'
}

def normalize_team_name(name: str) -> str:
    """Handles various team name formats from different APIs."""
    if not name: return name
    
    # Common nickname-to-full-name normalizations
    MAP = {
        "D-backs": "Arizona Diamondbacks",
        "Athletics": "Oakland Athletics",
        "Guardians": "Cleveland Guardians",
        "White Sox": "Chicago White Sox",
        "Red Sox": "Boston Red Sox",
        "Blue Jays": "Toronto Blue Jays"
    }
    
    name = name.strip()
    return MAP.get(name, name)

def get_team_elo(team_name: str) -> int:
    """Returns the current Elo rating for a team, prioritizes the dump file."""
    team_name = normalize_team_name(team_name)
    dump_path = os.path.join(os.path.dirname(__file__), 'elo_dump.json')
    
    if os.path.exists(dump_path):
        try:
            with open(dump_path, 'r') as f:
                data = json.load(f)
                # Map abbreviation back to full name or vice-versa
                for abbr, full in ABBR_MAP.items():
                    if full == team_name and abbr in data:
                        return int(data[abbr])
                
                # Check directly if the name is an abbreviation itself
                if team_name in data:
                    return int(data[team_name])
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Silently log error or handle here
            pass
            
    return ELO_BASES.get(team_name, 1500)

def load_elo_ratings() -> dict:
    """Returns the full dictionary of Team Name -> Elo Rating."""
    elo_dict = ELO_BASES.copy() # Start with baselines
    dump_path = os.path.join(os.path.dirname(__file__), 'elo_dump.json')
    
    if os.path.exists(dump_path):
        try:
            with open(dump_path, 'r') as f:
                data = json.load(f)
                for abbr, elo in data.items():
                    full_name = ABBR_MAP.get(abbr, abbr)
                    elo_dict[full_name] = int(elo)
        except (json.JSONDecodeError, ValueError):
            pass
            
    return elo_dict

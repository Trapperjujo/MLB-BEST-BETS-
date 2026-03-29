import json
import os

# 2026 MLB Opening Day Elo Ratings (Baseline)
# These represent team strength on March 29, 2026.
# Baseline is 1500.

ELO_BASES = {
    "Toronto Blue Jays": 1505,
    "New York Yankees": 1555,
    "Baltimore Orioles": 1565,
    "Tampa Bay Rays": 1515,
    "Boston Red Sox": 1495,
    "Houston Astros": 1545,
    "Los Angeles Dodgers": 1595,
    # ... other teams ...
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
    
    # Handle "Athletics" -> "Oakland Athletics"
    if name == "Athletics":
        return "Oakland Athletics"
    
    # Standard check
    return name

def get_team_elo(team_name: str) -> int:
    """Returns the current Elo rating for a team, prioritizes the dump file."""
    team_name = normalize_team_name(team_name)
    
    # Check for historical dump from pybaseball
    dump_path = os.path.join(os.path.dirname(__file__), 'elo_dump.json')
    if os.path.exists(dump_path):
        try:
            with open(dump_path, 'r') as f:
                data = json.load(f)
                # Map abbreviation back to full name or vice-versa
                for abbr, full in ABBR_MAP.items():
                    if full == team_name:
                        # Try the abbreviation in the data
                        if abbr in data:
                            return int(data[abbr])
                
                # Check directly if the name is an abbreviation itself
                if team_name in data:
                    return int(data[team_name])
        except:
            pass
            
    return ELO_BASES.get(team_name, 1500)

# MLB Home Field Advantage (HFA) Constant
MLB_HFA = 24

def load_elo_ratings() -> dict:
    """Returns the full dictionary of Team Name -> Elo Rating."""
    elo_dict = {}
    dump_path = os.path.join(os.path.dirname(__file__), 'elo_dump.json')
    
    # Priority: elo_dump.json (Historical calibrated)
    if os.path.exists(dump_path):
        try:
            with open(dump_path, 'r') as f:
                data = json.load(f)
                for abbr, elo in data.items():
                    # Map abbreviation back to full name
                    full_name = ABBR_MAP.get(abbr, abbr)
                    elo_dict[full_name] = int(elo)
        except:
            pass
            
    # Fill in any missing from ELO_BASES
    for name, elo in ELO_BASES.items():
        if name not in elo_dict:
            elo_dict[name] = elo
            
    return elo_dict

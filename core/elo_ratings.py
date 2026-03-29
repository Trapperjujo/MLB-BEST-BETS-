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

# Mapping for pybaseball abbreviations to full names
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
    'MIL': 'Milwaukee Brewers',
    'CHC': 'Chicago Cubs',
    'CIN': 'Cincinnati Reds',
    'STL': 'St. Louis Cardinals',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',
    'ARI': 'Arizona Diamondbacks',
    'SFG': 'San Francisco Giants',
    'COL': 'Colorado Rockies'
}

def get_team_elo(team_name: str) -> int:
    """Returns the current Elo rating for a team, prioritizes the dump file."""
    # Check for historical dump from pybaseball
    dump_path = os.path.join(os.path.dirname(__file__), 'elo_dump.json')
    if os.path.exists(dump_path):
        try:
            with open(dump_path, 'r') as f:
                data = json.load(f)
                # Map abbreviation back to full name or vice-versa
                # pybaseball uses abbreviations, app uses full names
                for abbr, full in ABBR_MAP.items():
                    if full == team_name:
                        return int(data.get(abbr, ELO_BASES.get(team_name, 1500)))
        except:
            pass
            
    return ELO_BASES.get(team_name, 1500)

# MLB Home Field Advantage (HFA) Constant
MLB_HFA = 24

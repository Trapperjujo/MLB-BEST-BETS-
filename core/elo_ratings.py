# 2026 MLB Opening Day Elo Ratings (Baseline)
# These represent team strength on March 29, 2026.
# Baseline is 1500.

ELO_RATINGS = {
    # AL East
    "Baltimore Orioles": 1565,
    "New York Yankees": 1555,
    "Tampa Bay Rays": 1515,
    "Toronto Blue Jays": 1505,
    "Boston Red Sox": 1495,
    
    # AL Central
    "Minnesota Twins": 1510,
    "Cleveland Guardians": 1500,
    "Detroit Tigers": 1490,
    "Kansas City Royals": 1475,
    "Chicago White Sox": 1420,
    
    # AL West
    "Houston Astros": 1545,
    "Texas Rangers": 1535,
    "Seattle Mariners": 1525,
    "Los Angeles Angels": 1470,
    "Oakland Athletics": 1410,
    
    # NL East
    "Atlanta Braves": 1585,
    "Philadelphia Phillies": 1550,
    "New York Mets": 1515,
    "Miami Marlins": 1485,
    "Washington Nationals": 1465,
    
    # NL Central
    "Milwaukee Brewers": 1520,
    "Chicago Cubs": 1510,
    "Cincinnati Reds": 1505,
    "St. Louis Cardinals": 1495,
    "Pittsburgh Pirates": 1480,
    
    # NL West
    "Los Angeles Dodgers": 1595,
    "San Diego Padres": 1530,
    "Arizona Diamondbacks": 1525,
    "San Francisco Giants": 1505,
    "Colorado Rockies": 1430
}

# MLB Home Field Advantage (HFA) Constant
MLB_HFA = 24

def get_team_elo(team_name: str) -> int:
    """Returns the current Elo rating for a team, or 1500 if unknown."""
    return ELO_RATINGS.get(team_name, 1500)

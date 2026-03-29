import pandas as pd
import os
import json

# Mapping for MLB.com Team Names to our Elo Abbreviations
TEAM_MAP = {
    'Arizona Diamondbacks': 'AZ', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL',
    'Boston Red Sox': 'BOS', 'Chicago Cubs': 'CHC', 'Chicago White Sox': 'CHW',
    'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KCR',
    'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA',
    'Milwaukee Brewers': 'MIL', 'Minnesota Twins': 'MIN', 'New York Mets': 'NYM',
    'New York Yankees': 'NYY', 'Oakland Athletics': 'OAK', 'Philadelphia Phillies': 'PHI',
    'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SD', 'San Francisco Giants': 'SF',
    'Seattle Mariners': 'SEA', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TBR',
    'Texas Rangers': 'TEX', 'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSN'
}

def calculate_multi_year_elo():
    """
    Back-calculates Elo ratings using local verified data.
    """
    elo_ratings = {abbr: 1500.0 for abbr in TEAM_MAP.values()}
    K = 20 # Elo K-factor
    
    file_path = "data/raw/mlb_official_2024.csv"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found. Run scrape_mlb_stats.py first.")
        return elo_ratings
        
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    
    print(f"Processing {len(df)} Games from Official 2024 Dataset...")
    
    for _, row in df.iterrows():
        home_name = row['home_team']
        away_name = row['away_team']
        
        # Map names to abbreviations
        home_abbr = TEAM_MAP.get(home_name)
        away_abbr = TEAM_MAP.get(away_name)
        
        if not home_abbr or not away_abbr:
            continue
            
        r_h = elo_ratings[home_abbr]
        r_a = elo_ratings[away_abbr]
        
        # Home win probability (with HFA adjustment of 24)
        e_h = 1 / (1 + 10**((r_a - (r_h + 24)) / 400))
        
        # Result: 1 if home won, 0 if away won
        if row['home_score'] > row['away_score']:
            s_h = 1
        elif row['home_score'] < row['away_score']:
            s_h = 0
        else:
            s_h = 0.5 # Tie
            
        # Update ratings
        elo_ratings[home_abbr] = r_h + K * (s_h - e_h)
        elo_ratings[away_abbr] = r_a + K * ((1 - s_h) - (1 - e_h))
        
    # Mean Reversion for season transition
    for abbr in elo_ratings:
        elo_ratings[abbr] = (elo_ratings[abbr] * 0.75) + (1500 * 0.25)
        
    # Save to file
    os.makedirs('core', exist_ok=True)
    with open('core/elo_dump.json', 'w') as f:
        json.dump(elo_ratings, f)
        
    return elo_ratings

if __name__ == "__main__":
    calculate_multi_year_elo()

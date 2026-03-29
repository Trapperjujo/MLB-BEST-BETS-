import pandas as pd
from pybaseball import schedule_and_record, team_ids
import time
from datetime import datetime

def calculate_multi_year_elo(seasons=[2024, 2025]):
    """
    Back-calculates Elo ratings starting from 1500 in 2024.
    Returns final Elo ratings for the start of 2026.
    """
    # Initialize all teams at 1500
    teams_list = team_ids()
    # Manual mapping for common team names to pybaseball abbreviations if needed
    # pybaseball uses abbreviations like 'TOR', 'NYY', etc.
    
    elo_ratings = {team: 1500 for team in [
        'AZ', 'ATL', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
        'HOU', 'KCR', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
        'PHI', 'PIT', 'SD', 'SF', 'SEA', 'STL', 'TBR', 'TEX', 'TOR', 'WSN'
    ]}
    
    K = 20 # Elo K-factor
    
    for season in seasons:
        print(f"Processing Season: {season}")
        all_games = []
        for team in elo_ratings.keys():
            try:
                sched = schedule_and_record(season, team)
                sched['Team'] = team
                all_games.append(sched)
                time.sleep(0.5) # Rate limiting safety
            except:
                print(f"Error fetching data for {team} in {season}")
        
        if not all_games:
            continue
            
        full_season = pd.concat(all_games)
        full_season['Date'] = pd.to_datetime(full_season['Date'].apply(lambda x: f"{x.split(', ')[1]} {season}"), format='%b %d %Y')
        full_season = full_season.sort_values(by='Date')
        
        # Process games (only once per game since schedule_and_record returns both sides)
        processed_games = set()
        
        for _, row in full_season.iterrows():
            date_key = f"{row['Date']}_{row['Team']}_{row['Opp']}"
            opp_date_key = f"{row['Date']}_{row['Opp']}_{row['Team']}"
            
            if date_key in processed_games or opp_date_key in processed_games:
                continue
            
            team_a = row['Team']
            team_b = row['Opp']
            # pybaseball 'Opp' is usually a team name or abbreviation. 
            # We need to map 'Opp' to our abbreviation keys.
            # For simplicity in this script, we'll assume abbreviations match.
            
            if team_a not in elo_ratings or team_b not in elo_ratings:
                continue
                
            r_a = elo_ratings[team_a]
            r_b = elo_ratings[team_b]
            
            e_a = 1 / (1 + 10**((r_b - r_a) / 400))
            
            # W/L result
            s_a = 1 if row['W/L'] == 'W' else 0
            
            elo_ratings[team_a] = r_a + K * (s_a - e_a)
            elo_ratings[team_b] = r_b + K * ((1 - s_a) - (1 - e_a))
            
            processed_games.add(date_key)
            
    # Mean Reversion (Standard Elo Practice: revert 1/3 towards 1500)
    for team in elo_ratings:
        elo_ratings[team] = (elo_ratings[team] * 0.75) + (1500 * 0.25)
        
    # Save to file
    import json
    with open('core/elo_dump.json', 'w') as f:
        json.dump(elo_ratings, f)
        
    return elo_ratings

if __name__ == "__main__":
    # This is a sample run. In production, we'd cache these.
    print("Initializing Multi-Year Elo Engine...")
    final_ratings = calculate_multi_year_elo()
    print("\n--- Final 2026 Opening Day Elo ---")
    for team, elo in sorted(final_ratings.items(), key=lambda x: x[1], reverse=True):
        print(f"{team}: {int(elo)}")

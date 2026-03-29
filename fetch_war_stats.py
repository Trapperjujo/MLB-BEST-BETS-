import pybaseball as pb
import pandas as pd
import os
import json

def fetch_and_save_war(year):
    print(f"Fetching Player-Level WAR for {year}...")
    try:
        # Batting stats with WAR
        print(f"  Fetching batting stats {year}...")
        batting = pb.batting_stats(year)
        # Select key columns for our model
        batting_reduced = batting[['Name', 'Team', 'WAR', 'IDfg']].copy()
        batting_reduced['Type'] = 'Batting'
        
        # Pitching stats with WAR
        print(f"  Fetching pitching stats {year}...")
        pitching = pb.pitching_stats(year)
        pitching_reduced = pitching[['Name', 'Team', 'WAR', 'IDfg']].copy()
        pitching_reduced['Type'] = 'Pitching'
        
        # Combine
        full_stats = pd.concat([batting_reduced, pitching_reduced], ignore_index=True)
        
        os.makedirs("data/raw", exist_ok=True)
        full_stats.to_csv(f"data/raw/player_war_{year}.csv", index=False)
        print(f"Saved WAR for {len(full_stats)} players to data/raw/player_war_{year}.csv")
        return full_stats
    except Exception as e:
        print(f"Error fetching WAR stats: {e}")
        return None

if __name__ == "__main__":
    fetch_and_save_war(2024)
    fetch_and_save_war(2025)

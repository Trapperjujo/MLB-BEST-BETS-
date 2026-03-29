import pandas as pd
import os

def audit_results():
    print("Starting Multi-Source Data Audit...")
    
    # 1. Load data
    mlb_file = "data/raw/mlb_official_2024.csv"
    api_file = "data/raw/api_sports_2024.csv"
    
    if not os.path.exists(mlb_file) or not os.path.exists(api_file):
        print("Missing audit files. Run scrapers first.")
        return
        
    df_mlb = pd.read_csv(mlb_file)
    df_api = pd.read_csv(api_file)
    
    # Standardize team names for comparison
    # (Simplified for this audit, in raw we trust the IDs or exact matches)
    print(f"  MLB.com Records: {len(df_mlb)}")
    print(f"  API-Sports Records: {len(df_api)}")
    
    # Merging on Game ID (PK) isn't possible directly as they use different IDs.
    # We use Date, Teams to match.
    # Normalize Date formats
    df_mlb['date'] = pd.to_datetime(df_mlb['date']).dt.strftime('%Y-%m-%d')
    df_api['date'] = pd.to_datetime(df_api['date']).dt.strftime('%Y-%m-%d')
    
    # Standardize Scores
    df_mlb['home_score'] = df_mlb['home_score'].fillna(0).astype(int)
    df_mlb['away_score'] = df_mlb['away_score'].fillna(0).astype(int)
    df_api['home_score'] = df_api['home_score'].fillna(0).astype(int)
    df_api['away_score'] = df_api['away_score'].fillna(0).astype(int)
    
    # Match analysis
    print("\n[Accuracy Audit Results]")
    matches = pd.merge(df_mlb, df_api, on=['date', 'home_team', 'away_team'], suffixes=('_mlb', '_api'))
    print(f"  Successfully matched games: {len(matches)}")
    
    discrepancies = matches[
        (matches['home_score_mlb'] != matches['home_score_api']) |
        (matches['away_score_mlb'] != matches['away_score_api'])
    ]
    
    print(f"  Discrepancies found: {len(discrepancies)}")
    if len(discrepancies) > 0:
        print(discrepancies[['date', 'home_team', 'away_team', 'home_score_mlb', 'home_score_api']].head())
    else:
        print("  ✅ Data sources are 100% consistent on matched scores.")

    # 2. Player WAR Audit
    war_2024 = pd.read_csv("data/raw/player_war_2024.csv")
    print(f"\n[Player Insight Audit]")
    print(f"  Total Players Tracked: {len(war_2024)}")
    top_players = war_2024.sort_values(by='WAR', ascending=False).head(5)
    print("  Top Performance Baseline (WAR):")
    print(top_players[['Name', 'Team', 'WAR']])
    
    return matches

if __name__ == "__main__":
    audit_results()

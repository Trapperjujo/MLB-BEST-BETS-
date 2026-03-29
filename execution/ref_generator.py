import pandas as pd
import numpy as np
import os
import json

def generate_reference_manual():
    print("Execution: Starting 3-Season Strategic Audit...")
    df = pd.read_csv('data/raw/master_history_2024_2026.csv')
    df = df[df['status'] == 'Final'].copy()
    
    # 1. Team Performance Matrix
    home_wins = df.groupby('home_team').apply(lambda x: (x['home_score'] > x['away_score']).mean(), include_groups=False)
    away_wins = df.groupby('away_team').apply(lambda x: (x['away_score'] > x['home_score']).mean(), include_groups=False)
    
    team_stats = {}
    teams = sorted(list(set(df['home_team'].unique()) | set(df['away_team'].unique())))
    
    for team in teams:
        team_stats[team] = {
            "overall_win_rate": float((home_wins.get(team, 0.5) + away_wins.get(team, 0.5)) / 2),
            "home_advantage": float(home_wins.get(team, 0.5) - 0.5),
            "avg_runs_scored": float((df[df['home_team'] == team]['home_score'].mean() + df[df['away_team'] == team]['away_score'].mean()) / 2)
        }
    
    # 2. Pitcher Tiers (top 50 by win frequency when starting)
    pitcher_games = []
    p_home = df[['home_pitcher', 'home_score', 'away_score']].rename(columns={'home_pitcher': 'pitcher', 'home_score': 'team_score', 'away_score': 'opp_score'})
    p_away = df[['away_pitcher', 'away_score', 'home_score']].rename(columns={'away_pitcher': 'pitcher', 'away_score': 'team_score', 'home_score': 'opp_score'})
    p_all = pd.concat([p_home, p_away])
    p_all = p_all[p_all['pitcher'] != 'TBD']
    
    p_stats = p_all.groupby('pitcher').apply(lambda x: pd.Series({
        "games": len(x),
        "win_rate": (x['team_score'] > x['opp_score']).mean()
    }), include_groups=False).reset_index()
    
    p_stats = p_stats[p_stats['games'] >= 10].sort_values(by='win_rate', ascending=False)
    pitcher_ref = p_stats.head(50).to_dict(orient='records')
    
    # 3. Seasonal Trends
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    monthly_scoring = df.groupby('month')['home_score'].mean() + df.groupby('month')['away_score'].mean()
    
    reference_data = {
        "metadata": {
            "total_games": len(df),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "seasons": [2024, 2025, 2026]
        },
        "team_matrix": team_stats,
        "elite_pitchers": pitcher_ref,
        "seasonal_scoring": monthly_scoring.to_dict()
    }
    
    os.makedirs('data/processed', exist_ok=True)
    with open('data/processed/reference_manual.json', 'w') as f:
        json.dump(reference_data, f, indent=4)
    
    print("REFERENCE MANUAL GENERATED: data/processed/reference_manual.json")

if __name__ == "__main__":
    from datetime import datetime
    generate_reference_manual()

import pandas as pd
import numpy as np
import sys
import os

# Ensure we can import from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.models import run_monte_carlo_simulation, calculate_elo_probability
from core.elo_ratings import get_team_elo, normalize_team_name

def perform_backtest():
    print("Execution: Starting Mathematical Audit: 2024 Seasonal Backtest...")
    df = pd.read_csv('data/raw/mlb_official_2024.csv')
    df = df[df['status'] == 'Final'].copy()
    
    results = []
    
    # Analyze a representative sample of 500 games for speed
    print(f"Processing {min(500, len(df))} game samples...")
    sample_df = df.sample(min(500, len(df)), random_state=42)
    
    for _, game in sample_df.iterrows():
        try:
            h_team = normalize_team_name(game["home_team"])
            a_team = normalize_team_name(game["away_team"])
            h_elo = get_team_elo(h_team)
            a_elo = get_team_elo(a_team)
            
            # Win Probability (Monte Carlo)
            prediction = run_monte_carlo_simulation(h_elo, a_elo, iterations=1000)
            h_prob = prediction['home_win_prob']
            
            # Actual Result
            h_win_actual = 1 if game['home_score'] > game['away_score'] else 0
            
            # Run Totals
            h_proj = prediction['home_avg_runs']
            a_proj = prediction['away_avg_runs']
            
            results.append({
                'h_prob': h_prob,
                'h_win_actual': h_win_actual,
                'h_score_actual': game['home_score'],
                'a_score_actual': game['away_score'],
                'h_proj': h_proj,
                'a_proj': a_proj
            })
        except Exception:
            continue
        
    res_df = pd.DataFrame(results)
    
    # 1. Predictive Accuracy
    res_df['correct'] = ((res_df['h_prob'] > 0.5) & (res_df['h_win_actual'] == 1)) | \
                       ((res_df['h_prob'] < 0.5) & (res_df['h_win_actual'] == 0))
    accuracy = res_df['correct'].mean()
    
    # 2. Brier Score (Mathematical Soundness of Probabilities)
    brier = np.mean((res_df['h_prob'] - res_df['h_win_actual'])**2)
    
    # 3. RMSE (Score Accuracy)
    h_rmse = np.sqrt(np.mean((res_df['h_proj'] - res_df['h_score_actual'])**2))
    a_rmse = np.sqrt(np.mean((res_df['a_proj'] - res_df['a_score_actual'])**2))
    
    print("\n--- Summary: Audit Results ---")
    print(f"Win/Loss Accuracy: {accuracy:.2%}")
    print(f"Brier Score: {brier:.4f}")
    print(f"Home Score RMSE: {h_rmse:.2f} runs")
    print(f"Away Score RMSE: {a_rmse:.2f} runs")
    
    # Calibration Check
    print("\n--- Summary: Calibration Check ---")
    bins = [0.3, 0.4, 0.5, 0.6, 0.7]
    for b in bins:
        subset = res_df[(res_df['h_prob'] >= b) & (res_df['h_prob'] < b + 0.1)]
        if not subset.empty:
            actual_win_rate = subset['h_win_actual'].mean()
            print(f"Bin {int(b*100)}-{int(b*100+10)}%: Actual Win Rate {actual_win_rate:.2%}")

if __name__ == "__main__":
    perform_backtest()

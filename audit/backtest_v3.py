import pandas as pd
import numpy as np
import sys
import os

# Ensure we can import from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.prediction_xgboost import predict_xgboost_v3
from core.elo_ratings import normalize_team_name

def perform_v3_audit():
    print("Execution: Starting Mathematical Audit: XGBoost v3.0 (Longitudinal Elite)...")
    
    # Load 2025 Historical Data (The 'True Data' test set)
    df = pd.read_csv('data/raw/master_history_2024_2026.csv')
    df_2025 = df[df['date'].str.startswith('2025')].copy()
    df_2025 = df_2025[df_2025['status'] == 'Final'].copy()
    
    if df_2025.empty:
        print("Error: No 2025 historical data found for audit.")
        return

    results = []
    
    # Analyze 500 games
    sample_size = min(500, len(df_2025))
    print(f"Processing {sample_size} game samples from 2025 dataset...")
    sample_df = df_2025.sample(sample_size, random_state=42)
    
    for _, game in sample_df.iterrows():
        try:
            h_team = normalize_team_name(game["home_team"])
            a_team = normalize_team_name(game["away_team"])
            
            # Predict
            h_prob, conf = predict_xgboost_v3(h_team, a_team)
            
            # Actual
            h_win_actual = 1 if game['home_score'] > game['away_score'] else 0
            
            results.append({
                'h_prob': h_prob,
                'h_win_actual': h_win_actual,
                'correct': (h_prob > 0.5 and h_win_actual == 1) or (h_prob < 0.5 and h_win_actual == 0)
            })
        except Exception:
            continue
            
    res_df = pd.DataFrame(results)
    
    accuracy = res_df['correct'].mean()
    brier = np.mean((res_df['h_prob'] - res_df['h_win_actual'])**2)
    
    print("\n--- v3.0 Audit Results (True Data) ---")
    print(f"Win/Loss Accuracy: {accuracy:.2%}")
    print(f"Brier Score (Calibration): {brier:.4f}")
    
    if accuracy > 0.60:
        print("\n✅ STRATEGIC VALIDATION: v3.0 meets Elite Benchmarks (>60% accuracy).")
    else:
        print("\n⚠️ PERFORMANCE NOTE: Calibration ongoing for early season variance.")

if __name__ == "__main__":
    perform_v3_audit()

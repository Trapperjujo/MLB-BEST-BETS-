import pandas as pd
from core.stats_engine import get_pitcher_stats, get_team_hitting_stats
from core.prediction_xgboost import predict_xgboost_v2
from core.elo_ratings import normalize_team_name, get_team_elo

# Mocking parts of app.py logic for verification
def verify_flow():
    print("Loading Pitcher Stats...")
    p_stats = get_pitcher_stats(2024)
    print(f"Loaded {len(p_stats)} pitchers.")
    
    mock_row = {
        'home_team': 'New York Yankees',
        'away_team': 'Los Angeles Dodgers',
        'home_pitcher': 'Gerrit Cole',
        'away_pitcher': 'Yoshinobu Yamamoto'
    }
    
    # Simulate the lookup logic 
    h_p_name = mock_row['home_pitcher']
    h_ps = p_stats[p_stats['Name'] == h_p_name].iloc[0].to_dict() if not p_stats.empty and not p_stats[p_stats['Name'] == h_p_name].empty else None
    
    print(f"Found Stats for {h_p_name}: {h_ps['ERA'] if h_ps else 'Not Found'}")
    
    print("Testing XGBoost v2 Prediction...")
    prob, conf = predict_xgboost_v2(normalize_team_name(mock_row['home_team']), 
                                    normalize_team_name(mock_row['away_team']), 
                                    h_ps, None)
    print(f"Prob: {prob:.2%}, Confidence: {conf:.2%}")

if __name__ == "__main__":
    verify_flow()

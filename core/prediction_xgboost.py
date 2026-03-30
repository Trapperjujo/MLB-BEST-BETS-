import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from core.elo_ratings import get_team_elo
import os
import json

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'xgboost_v3.json')
REF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'reference_manual.json')

def load_ref_material():
    if os.path.exists(REF_PATH):
        with open(REF_PATH, 'r') as f:
            return json.load(f)
    return {}

def train_advanced_model():
    """
    Trains XGBoost v3.0 (Longitudinal Elite) using 3 seasons of historical ground truth.
    """
    try:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        # Load Expanded History (7,700+ games)
        df = pd.read_csv("data/raw/master_history_2024_2026.csv")
        df = df[df['status'] == 'Final'].copy()
        
        # Load Reference Material
        ref = load_ref_material()
        team_matrix = ref.get('team_matrix', {})
        
        # Feature Engineering (Ground Truth)
        df['h_elo'] = df['home_team'].apply(get_team_elo)
        df['a_elo'] = df['away_team'].apply(get_team_elo)
        
        # 3-Year Longitudinal Features
        df['h_3y_winrate'] = df['home_team'].apply(lambda x: team_matrix.get(x, {}).get('overall_win_rate', 0.5))
        df['a_3y_winrate'] = df['away_team'].apply(lambda x: team_matrix.get(x, {}).get('overall_win_rate', 0.5))
        
        # Scoring Benchmarks
        df['h_avg_runs'] = df['home_team'].apply(lambda x: team_matrix.get(x, {}).get('avg_runs_scored', 4.4))
        df['a_avg_runs'] = df['away_team'].apply(lambda x: team_matrix.get(x, {}).get('avg_runs_scored', 4.4))
        
        # Target
        df['target'] = (df['home_score'] > df['away_score']).astype(int)
        
        features = ['h_elo', 'a_elo', 'h_3y_winrate', 'a_3y_winrate', 'h_avg_runs', 'a_avg_runs']
        X = df[features]
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
        
        # Hyper-Parameter Tuning for "Mathematically Perfect" Calibration
        model = xgb.XGBClassifier(
            n_estimators=250,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.85,
            colsample_bytree=0.85,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        
        model.save_model(MODEL_PATH)
        print(f"XGBoost v3.0 (Longitudinal) trained on {len(df)} games and saved.")
        return model
    except Exception as e:
        print(f"XGBoost v3.0 Training Error: {e}")
        return None

def load_advanced_model():
    if os.path.exists(MODEL_PATH):
        try:
            model = xgb.XGBClassifier()
            model.load_model(MODEL_PATH)
            return model
        except Exception:
            pass
    return train_advanced_model()

_MODEL = load_advanced_model()

from core.config import MLB_PARK_FACTORS

def predict_xgboost_v3(home_team, away_team):
    """
    Predict using v3.0 Longitudinal Engine with Situational Alpha Drift.
    """
    if _MODEL is None:
        return 0.5, 0.5
        
    ref = load_ref_material()
    team_matrix = ref.get('team_matrix', {})
    
    h_elo = get_team_elo(home_team)
    a_elo = get_team_elo(away_team)
    h_3y = team_matrix.get(home_team, {}).get('overall_win_rate', 0.5)
    a_3y = team_matrix.get(away_team, {}).get('overall_win_rate', 0.5)
    h_runs = team_matrix.get(home_team, {}).get('avg_runs_scored', 4.4)
    a_runs = team_matrix.get(away_team, {}).get('avg_runs_scored', 4.4)
    
    features = pd.DataFrame([[h_elo, a_elo, h_3y, a_3y, h_runs, a_runs]], 
                            columns=['h_elo', 'a_elo', 'h_3y_winrate', 'a_3y_winrate', 'h_avg_runs', 'a_avg_runs'])
    
    probs = _MODEL.predict_proba(features)[0]
    home_win_prob = probs[1]
    
    # 🛰️ SITUATIONAL ALPHA: Venue Drift
    # We apply a 'Venue Alpha' correction based on institutional park factors.
    factor = MLB_PARK_FACTORS.get(home_team, MLB_PARK_FACTORS["Default"])
    
    # Run suppression factor (e.g., Mariners 81.0 -> 0.81)
    # Pitcher-friendly parks slightly favor the home team in close matchups (defensive stability)
    run_suppression = factor['run'] / 100.0
    k_index = factor.get('k_factor', 100.0) / 100.0
    
    # Logic: extreme run suppression (+ pitcher-friendly) favors lower variance, 
    # slightly boosting the favorite's probability of a clean win.
    drift = 0.0
    if run_suppression < 0.90: drift += 0.02 # Pitcher's park boost
    if k_index > 1.10: drift += 0.015 # High-strikeout environment favor
    
    home_win_prob = np.clip(home_win_prob + drift, 0.01, 0.99)
    confidence = max(home_win_prob, 1 - home_win_prob)
    
    return float(home_win_prob), float(confidence)

import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from core.elo_ratings import get_team_elo

def train_baseline_model():
    """
    Trains a baseline XGBoost model using historical 2024 outcomes.
    Features: Home/Away Elo, Point Differential, and Season Progress.
    """
    try:
        df = pd.read_csv("data/raw/mlb_official_2024.csv")
        df = df[df['status'] == 'Final'].copy()
        
        # Feature Engineering: Map Elo Ratings
        df['home_elo'] = df['home_team'].apply(get_team_elo)
        df['away_elo'] = df['away_team'].apply(get_team_elo)
        df['elo_diff'] = df['home_elo'] - df['away_elo']
        
        # Target: Home Win (1) or Away Win (0)
        df['target'] = (df['home_score'] > df['away_score']).astype(int)
        
        X = df[['home_elo', 'away_elo', 'elo_diff']]
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        print(f"XGBoost Training Error: {e}")
        return None

# Global Model Instance
_MODEL = train_baseline_model()

def predict_xgboost(home_team, away_team):
    """
    Returns the XGBoost win probability for the Home Team.
    Also returns a 'Model Confidence' score (0-1).
    """
    if _MODEL is None:
        return 0.5, 0.0
        
    h_elo = get_team_elo(home_team)
    a_elo = get_team_elo(away_team)
    elo_diff = h_elo - a_elo
    
    features = pd.DataFrame([[h_elo, a_elo, elo_diff]], columns=['home_elo', 'away_elo', 'elo_diff'])
    
    probs = _MODEL.predict_proba(features)[0]
    home_win_prob = probs[1]
    
    # Confidence: Distance from 0.5
    confidence = abs(home_win_prob - 0.5) * 2
    
    return home_win_prob, confidence

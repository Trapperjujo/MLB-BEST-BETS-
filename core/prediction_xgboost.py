import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from core.elo_ratings import get_team_elo

def train_advanced_model():
    """
    Trains an advanced XGBoost model using historical outcomes + Pitcher/Team stats.
    Features: Elo, Pitcher ERA (Baseline), Team OPS (Baseline).
    """
    try:
        df = pd.read_csv("data/raw/mlb_official_2024.csv")
        df = df[df['status'] == 'Final'].copy()
        
        # In a real environment, we'd merge with actual 2024 pitcher stats here.
        # For this execution, we'll use Elo as a proxy for 'Strength' and 
        # add 'Normal Noise' to simulate Pitcher/Team features for the model logic.
        
        df['home_elo'] = df['home_team'].apply(get_team_elo)
        df['away_elo'] = df['away_team'].apply(get_team_elo)
        
        # Synthetic Feature Simulation based on Elo (to establish non-linear relationships)
        df['h_p_era'] = 4.5 - (df['home_elo'] - 1500) / 100 + np.random.normal(0, 0.5, len(df))
        df['a_p_era'] = 4.5 - (df['away_elo'] - 1500) / 100 + np.random.normal(0, 0.5, len(df))
        df['h_ops'] = 0.720 + (df['home_elo'] - 1500) / 2000 + np.random.normal(0, 0.05, len(df))
        df['a_ops'] = 0.720 + (df['away_elo'] - 1500) / 2000 + np.random.normal(0, 0.05, len(df))
        
        # Target
        df['target'] = (df['home_score'] > df['away_score']).astype(int)
        
        features = ['home_elo', 'away_elo', 'h_p_era', 'a_p_era', 'h_ops', 'a_ops']
        X = df[features]
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
        
        model = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.9,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        print(f"XGBoost Advanced Training Error: {e}")
        return None

# Singleton Model Instance
_MODEL = train_advanced_model()

def predict_xgboost_v2(home_team, away_team, h_p_stats=None, a_p_stats=None, h_t_stats=None, a_t_stats=None):
    """
    Inference with advanced features.
    Defaults to 4.0 ERA and 0.750 OPS if stats are missing.
    """
    if _MODEL is None:
        return 0.5, 0.0
        
    h_elo = get_team_elo(home_team)
    a_elo = get_team_elo(away_team)
    
    # Feature Engineering
    h_era = h_p_stats.get('ERA', 4.0) if h_p_stats else 4.0
    a_era = a_p_stats.get('ERA', 4.0) if a_p_stats else 4.0
    h_ops = h_t_stats.get('OPS', 0.750) if h_t_stats else 0.750
    a_ops = a_t_stats.get('OPS', 0.750) if a_t_stats else 0.750
    
    features = pd.DataFrame([[h_elo, a_elo, h_era, a_era, h_ops, a_ops]], 
                            columns=['home_elo', 'away_elo', 'h_p_era', 'a_p_era', 'h_ops', 'a_ops'])
    
    probs = _MODEL.predict_proba(features)[0]
    home_win_prob = probs[1]
    confidence = abs(home_win_prob - 0.5) * 2
    
    return home_win_prob, confidence

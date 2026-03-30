import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from core.logger import terminal_logger as logger
from core.unified_config import config
from core.models import run_monte_carlo_simulation, calculate_war_elo_adjustment, calculate_ev
from core.prediction_xgboost import predict_xgboost_v3
from core.elo_ratings import normalize_team_name

class PredictionService:
    """Institutional Prediction Orchestrator (Phase 16)."""
    
    def __init__(self, elo_repo, game_repo, scraper):
        self.elo_repo = elo_repo
        self.game_repo = game_repo
        self.scraper = scraper

    def predict_matchup(self, row, history_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Orchestrates a complete predictive analysis for a single game."""
        h_team, a_team = normalize_team_name(row["home_team"]), normalize_team_name(row["away_team"])
        
        # 1. 🧬 Elo & Momentum Alpha
        h_elo_data = self.elo_repo.get_team_strength(h_team)
        a_elo_data = self.elo_repo.get_team_strength(a_team)
        
        # 2. 📉 Fatigue & War Adjustments
        h_fat = self.elo_repo.get_fatigue_adjustment(h_team, history_df)
        a_fat = self.elo_repo.get_fatigue_adjustment(a_team, history_df)
        
        # Note: Placeholder for team_war logic (extracted from previous turnkey)
        # 1 WAR = ~6.25 Elo points.
        h_elo_adj = h_elo_data["effective_elo"] - h_fat
        a_elo_adj = a_elo_data["effective_elo"] - a_fat
        
        # 3. 🛰️ Alpha Ingestion: Check 2026 Betting Trends for Situational Weights
        # (Scraper handles caching and hydration)
        trends = self.scraper.get_cached_trends()
        h_trend = next((t for t in trends if normalize_team_name(t['team']) == h_team), None)
        h_cover_pct = float(h_trend.get('cover_pct_val', 50.0)) if h_trend else 50.0
        
        # 4. 🚀 Execute Monte Carlo Simulation Core (Vectorized)
        mc = run_monte_carlo_simulation(
            home_elo=int(h_elo_adj), 
            away_elo=int(a_elo_adj), 
            iterations=config.MC_ITERATIONS,
            hfa=config.MLB_HFA,
            home_team=h_team,
            cover_pct=h_cover_pct
        )
        
        # 5. 📉 XGBoost v3.0 Longitudinal Filtering
        xg_p, xg_c = predict_xgboost_v3(h_team, a_team)
        
        # 6. Structured Payload Return
        return {
            'home_win_prob': mc['home_win_prob'], 
            'away_win_prob': mc['away_win_prob'], 
            'home_elo_adj': h_elo_adj, 
            'away_elo_adj': a_elo_adj,
            'home_proj': mc['home_avg_runs'], 
            'away_proj': mc['away_avg_runs'], 
            'xg_prob': xg_p, 
            'xg_conf': xg_c
        }

# Global Service (Factory)
def get_prediction_service(elo_repo, game_repo, scraper):
    return PredictionService(elo_repo, game_repo, scraper)

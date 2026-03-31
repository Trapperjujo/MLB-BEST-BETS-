import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from core.logger import terminal_logger as logger
import core.unified_config as config
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
        """
        🚀 Triple-Source Prediction Pipeline:
        Combines Base Elo (Layer 3) + Scraper Trends (Layer 2) + DuckDB Glossary Alpha.
        """
        h_team, a_team = normalize_team_name(row["home_team"]), normalize_team_name(row["away_team"])
        
        # 1. 🧬 Elo & Momentum Alpha
        h_elo_data = self.elo_repo.get_team_strength(h_team)
        a_elo_data = self.elo_repo.get_team_strength(a_team)
        
        # 2. 📉 Fatigue & Base Adjustments
        h_fat = self.elo_repo.get_fatigue_adjustment(h_team, history_df)
        a_fat = self.elo_repo.get_fatigue_adjustment(a_team, history_df)
        
        h_elo_adj = h_elo_data["effective_elo"] - h_fat
        a_elo_adj = a_elo_data["effective_elo"] - a_fat
        
        # 🛡️ LAYER 3 ALPHA: DuckDB Glossary Integration
        # We perform an 'Elo-Alpha' adjustment based on advanced peripheral metrics.
        try:
            from core.database import terminal_db
            
            # Fetch situational peripherals
            h_metrics = terminal_db.conn.execute("SELECT * FROM glossary_batting_2026 WHERE Team = ?", [h_team]).fetchdf()
            a_metrics = terminal_db.conn.execute("SELECT * FROM glossary_batting_2026 WHERE Team = ?", [a_team]).fetchdf()
            
            # Example: wRC+ Momentum Adjustment (+1 Elo for every point above 100)
            if not h_metrics.empty:
                wrc_plus = float(h_metrics.iloc[0].get('wRC+', 100))
                h_elo_adj += (wrc_plus - 100) * 0.2
            if not a_metrics.empty:
                wrc_plus = float(a_metrics.iloc[0].get('wRC+', 100))
                a_elo_adj += (wrc_plus - 100) * 0.2
                
            # Fielding Adjustment (DRS/OAA)
            h_fielding = terminal_db.conn.execute("SELECT DRS, OAA FROM glossary_fielding_2026 WHERE Team = ?", [h_team]).fetchdf()
            if not h_fielding.empty:
                drs = float(h_fielding.iloc[0].get('DRS', 0))
                h_elo_adj += drs * 0.5 # 1 DRS = 0.5 Elo points roughly
                
        except Exception as e:
            logger.debug(f"Glossary Alpha Ingestion Skipped: {e}")

        # 3. 🛰️ LAYER 2 ALPHA: Scraper Betting Trends
        trends = self.scraper.get_cached_trends()
        h_trend = next((t for t in trends if normalize_team_name(t['team']) == h_team), None)
        h_cover_pct = float(h_trend.get('cover_pct_val', 50.0)) if h_trend else 50.0
        
        # 🏛️ NEW: LAYER 4 ALPHA: Official MLB Ground Truth Anchor
        h_win_pct = 0.500
        try:
            h_off = terminal_db.conn.execute("SELECT WinPct FROM official_standings_2026 WHERE Team = ?", [h_team]).fetchdf()
            if not h_off.empty:
                h_win_pct = float(h_off.iloc[0]['WinPct'])
        except:
            pass

        # 4. 🚀 Execute Monte Carlo Simulation Core (70/30 Hybrid)
        mc = run_monte_carlo_simulation(
            home_elo=int(h_elo_adj), 
            away_elo=int(a_elo_adj), 
            iterations=config.MC_ITERATIONS,
            hfa=config.MLB_HFA,
            home_team=h_team,
            cover_pct=h_cover_pct,
            official_win_pct=h_win_pct
        )
        
        # 5. 📉 XGBoost v3.0 Filtering
        xg_p, xg_c = predict_xgboost_v3(h_team, a_team)
        
        return {
            'home_team': h_team,
            'away_team': a_team,
            'home_win_prob': mc['home_win_prob'], 
            'away_win_prob': mc['away_win_prob'], 
            'home_elo': h_elo_adj, 
            'away_elo': a_elo_adj,
            'h_raw_elo': h_base, # Raw Process Metric (Advanced)
            'h_official_win_pct': h_win_pct, # Results Metric (Official)
            'home_proj': mc['home_avg_runs'], 
            'away_proj': mc['away_avg_runs'], 
            'xg_prob': xg_p, 
            'xg_conf': xg_c,
            'h_p_era': 4.5, # Defaults for 2026 Opening
            'a_p_era': 4.5,
            'home_scores_sample': mc['home_scores'],
            'away_scores_sample': mc['away_scores']
        }

# Global Service (Factory)
def get_prediction_service(elo_repo, game_repo, scraper):
    return PredictionService(elo_repo, game_repo, scraper)

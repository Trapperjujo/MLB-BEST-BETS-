import os
import math
import json
import logging
import pandas as pd
import numpy as np
from core.elo_ratings import ABBR_MAP, normalize_team_name, get_team_elo
from core.status_fetcher import get_fatigue_penalty
from core.models import calculate_war_elo_adjustment, run_monte_carlo_simulation
from core.prediction_xgboost import predict_xgboost_v3
from core.config import MC_ITERATIONS, MLB_HFA

logger = logging.getLogger(__name__)

def load_team_war_map():
    """Loads and maps team WAR totals for 2025/2026 baseline."""
    path = "data/raw/player_war_2025.csv"
    if not os.path.exists(path):
        logger.warning(f"WAR data path not found: {path}")
        return {}
    
    try:
        df = pd.read_csv(path)
        team_war = df.groupby('Team')['WAR'].sum().to_dict()
        full_team_war = {}
        for team, war in team_war.items():
            full_name = ABBR_MAP.get(team, team)
            full_team_war[full_name] = war
        return full_team_war
    except Exception as e:
        logger.error(f"Error loading WAR map: {e}")
        return {}

def get_prediction(row, history_df: pd.DataFrame = None, **kwargs):
    """
    Orchestrates the predictive engine for a single matchup.
    Combines Elo, Momentum Alpha, Fatigue, and XGBoost projections.
    """
    h_p_stats = kwargs.get('p_stats', pd.DataFrame())
    a_p_stats = kwargs.get('p_stats', pd.DataFrame()) # Note: in app.py it was also p_stats
    h_p_name, a_p_name = row.get('home_pitcher', 'TBD'), row.get('away_pitcher', 'TBD')
    h_team, a_team = normalize_team_name(row["home_team"]), normalize_team_name(row["away_team"])
    
    # 🛰️ Extract services/trackers from kwargs
    tracker = kwargs.get('tracker')
    scraper = kwargs.get('scraper')
    team_war_map = kwargs.get('team_war_map', {})
    standings = kwargs.get('standings_df', pd.DataFrame())
    
    # 📡 Hybrid Elo Alignment & 2026 Momentum Alpha
    h_elo, a_elo = get_team_elo(h_team), get_team_elo(a_team)
    h_fat, a_fat = get_fatigue_penalty(h_team, history_df), get_fatigue_penalty(a_team, history_df)
    
    # Live Standings Momentum Adjustment
    h_mom, a_mom = 0, 0
    if not standings.empty:
        h_rec = standings[standings['Team'] == h_team]
        a_rec = standings[standings['Team'] == a_team]
        if not h_rec.empty:
            # Momentum Alpha: Win% deviation from .500 * March phase weight (10.0)
            h_mom = int((float(h_rec.iloc[0]['PCT']) - 0.500) * 10)
        if not a_rec.empty:
            a_mom = int((float(a_rec.iloc[0]['PCT']) - 0.500) * 10)
    
    h_war, a_war = float(team_war_map.get(h_team, 0.0)), float(team_war_map.get(a_team, 0.0))
    w_adj = calculate_war_elo_adjustment(h_war, a_war)

    # 📏 Final Calibration: (Base Elo + Momentum) - Fatigue + WAR
    h_base = float(h_elo or 1500)
    a_base = float(a_elo or 1500)
    h_fat_val = float(h_fat or 0)
    a_fat_val = float(a_fat or 0)
    
    w_val = float(w_adj) if w_adj is not None and not pd.isna(w_adj) else 0.0
    
    h_elo_adj = h_base + float(h_mom) - h_fat_val + max(0.0, w_val)
    a_elo_adj = a_base + float(a_mom) - a_fat_val + abs(min(0.0, w_val))

    if pd.isna(h_elo_adj) or np.isinf(h_elo_adj): h_elo_adj = 1500.0
    if pd.isna(a_elo_adj) or np.isinf(a_elo_adj): a_elo_adj = 1500.0

    h_ps = h_p_stats[h_p_stats['Name'] == h_p_name].iloc[0].to_dict() if not h_p_stats.empty and not h_p_stats[h_p_stats['Name'] == h_p_name].empty else None
    a_ps = a_p_stats[a_p_stats['Name'] == a_p_name].iloc[0].to_dict() if not a_p_stats.empty and not a_p_stats[a_p_stats['Name'] == a_p_name].empty else None

    # 🛰️ Alpha Ingestion: Check 2026 Betting Trends for Situational Weights
    h_cover_pct = 50.0
    if scraper:
        try:
            trends_raw = scraper.scrape_betting_trends() if not os.path.exists(scraper.cache_path) else json.load(open(scraper.cache_path))['trends']
            h_trend = next((t for t in trends_raw if normalize_team_name(t['team']) == normalize_team_name(h_team)), None)
            h_cover_pct = float(h_trend.get('cover_pct_val', 50.0)) if h_trend else 50.0
        except Exception as e:
            logger.error(f"Error scraping betting trends in prediction service: {e}")

    # 🛰️ Execute Monte Carlo Simulation Core
    mc = run_monte_carlo_simulation(
        home_elo=int(h_elo_adj), 
        away_elo=int(a_elo_adj), 
        iterations=MC_ITERATIONS,
        hfa=MLB_HFA,
        home_team=h_team,
        cover_pct=h_cover_pct
    )
    
    # 🛰️ SHADOW-MODE BASALINE (Poisson Comparison)
    p_baseline = 1.0 / (1.0 + math.pow(10.0, (int(a_elo_adj) - (int(h_elo_adj) + MLB_HFA)) / 400.0))
    
    if tracker:
        tracker.track_event("shadow_audit_capture", {
            "away": a_team, "home": h_team,
            "nb_model_prob": mc['home_win_prob'],
            "poisson_baseline": p_baseline,
            "alpha_yield": mc['home_win_prob'] - p_baseline
        })

    xg_p, xg_c = predict_xgboost_v3(h_team, a_team)
    return {
        'home_win_prob': mc['home_win_prob'], 
        'away_win_prob': mc['away_win_prob'], 
        'home_elo': h_base, 
        'away_elo': a_base,
        'home_proj': mc['home_avg_runs'], 
        'away_proj': mc['away_avg_runs'], 
        'home_scores_sample': mc['home_scores'], 
        'away_scores_sample': mc['away_scores'],
        'xg_prob': xg_p, 
        'xg_conf': xg_c, 
        'h_p_era': h_ps.get('ERA', 4.0) if h_ps else 4.0, 
        'a_p_era': a_ps.get('ERA', 4.0) if a_ps else 4.0
    }

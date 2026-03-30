import os
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from core.config import (
    DEPLOYMENT_VERSION, 
    BANKROLL_DEFAULT, 
    MAX_STAKE_CAP, 
    STD_BET_SIZE_DEFAULT,
    MIN_EDGE_DEFAULT
)
from core.data_fetcher import get_rapid_odds, process_rapid_odds, get_mlb_schedule, get_tank01_scores
from core.stats_engine import get_2026_standings, get_2026_leaders, get_pitcher_stats, get_team_hitting_stats
from core.elo_ratings import normalize_team_name
from core.models import (
    calculate_ev, 
    calculate_implied_probability, 
    american_to_decimal, 
    calculate_sport_select_ev, 
    kelly_criterion, 
    calculate_fair_odds
)
from core.prediction_service import get_prediction, load_team_war_map
from core.strategy import is_divisional_matchup

logger = logging.getLogger(__name__)

def sync_mlb_data(bankroll: float, fractional_kelly: float, reduction_factor: float, status_callback=None):
    """
    Orchestrates the synchronization of MLB schedule, odds, standings, and predictions.
    This is the core data pipeline for the terminal.
    """
    t = datetime.now()
    cur_date = t.strftime("%Y-%m-%d")
    nxt_date = (t + timedelta(days=1)).strftime("%Y-%m-%d")
    prev_date = (t - timedelta(days=3)).strftime("%Y-%m-%d")
    
    if status_callback: status_callback("📡 Fetching MLB Schedule...")
    
    full_sched = get_mlb_schedule(cur_date) + get_mlb_schedule(nxt_date)
    if not full_sched:
        logger.error("Failed to fetch MLB schedule.")
        return pd.DataFrame(), {}, {}, {}
    
    df_sched = pd.DataFrame(full_sched)
    hist_raw = get_mlb_schedule(start_date=prev_date, end_date=cur_date)
    df_hist = pd.DataFrame(hist_raw) if hist_raw else pd.DataFrame()
    
    if status_callback: status_callback("🎲 Processing Market Odds...")
    raw_odds = get_rapid_odds(t.strftime("%Y%m%d"))
    df_odds = process_rapid_odds(raw_odds) if raw_odds.get("data") else pd.DataFrame()
    
    if status_callback: status_callback("📊 Loading Standings & Stats...")
    df_p = get_pitcher_stats(2026) if not get_pitcher_stats(2026).empty else get_pitcher_stats(2025)
    df_t = get_team_hitting_stats(2026) if not get_team_hitting_stats(2026).empty else get_team_hitting_stats(2025)
    df_standings = get_2026_standings()
    df_leaders = get_2026_leaders()
    
    live_data = get_tank01_scores(t.strftime("%Y%m%d"))
    live_scores = live_data.get("body", {}) if live_data else {}
    
    df_sched["h_norm"] = df_sched["home_team"].apply(normalize_team_name)
    df_sched["a_norm"] = df_sched["away_team"].apply(normalize_team_name)
    
    team_war_map = load_team_war_map()
    
    if status_callback: status_callback("🧬 Running Predictive Models...")
    
    # We use a wrapper to pass the services/context to get_prediction
    preds = df_sched.apply(
        lambda r: pd.Series(
            get_prediction(
                r, 
                df_hist, 
                p_stats=df_p, 
                t_stats=df_t, 
                standings_df=df_standings,
                team_war_map=team_war_map
            )
        ), 
        axis=1
    )
    df_sched = pd.concat([df_sched, preds], axis=1)
    
    final_rows = []
    for _, g in df_sched.iterrows():
        # Match schedule with odds
        if not df_odds.empty:
            match = df_odds[
                (df_odds["home_team"].apply(normalize_team_name) == g["h_norm"]) & 
                (df_odds["away_team"].apply(normalize_team_name) == g["a_norm"])
            ]
            if not match.empty:
                for _, o in match.iterrows():
                    nr = g.to_dict()
                    nr.update({
                        "bookmaker": o["bookmaker"], 
                        "outcome": o["outcome"], 
                        "odds": o["odds"], 
                        "market": o["market"]
                    })
                    ih = (normalize_team_name(o["outcome"]) == g["h_norm"])
                    nr["model_prob"] = g["home_win_prob"] if ih else g["away_win_prob"]
                    nr["team_elo"] = g["home_elo"] if ih else g["away_elo"]
                    nr["opp_elo"] = g["away_elo"] if ih else g["home_elo"]
                    nr["team_proj"] = g["home_proj"] if ih else g["away_proj"]
                    nr["opp_proj"] = g["away_proj"] if ih else g["home_proj"]
                    final_rows.append(nr)
                continue
        
        # Fallback to default/pending odds if no market match
        nr = g.to_dict()
        nr.update({
            "bookmaker": "Pending", 
            "outcome": g["home_team"], 
            "odds": None, 
            "market": "h2h", 
            "model_prob": g["home_win_prob"], 
            "team_elo": g["home_elo"], 
            "opp_elo": g["away_elo"], 
            "team_proj": g["home_proj"], 
            "opp_proj": g["away_proj"]
        })
        final_rows.append(nr)
    
    df_final = pd.DataFrame(final_rows)
    
    if not df_final.empty:
        df_final["is_divisional"] = df_final.apply(lambda r: is_divisional_matchup(r["home_team"], r["away_team"]), axis=1)
        df_final["formatted_time"] = pd.to_datetime(df_final["commence_time"]).dt.strftime("%a, %b %d @ %I:%M %p")
        
        ho_mask = df_final["odds"].notnull()
        df_final.loc[ho_mask, "implied_prob"] = df_final.loc[ho_mask, "odds"].apply(calculate_implied_probability)
        df_final.loc[ho_mask, "decimal_odds"] = df_final.loc[ho_mask, "odds"].apply(american_to_decimal)
        df_final.loc[ho_mask, "data_type"] = "💎 Multi-Source Alpha Yield"
        
        no_mask = df_final["odds"].isnull()
        df_final.loc[no_mask, "decimal_odds"] = 1.91
        df_final.loc[no_mask, "implied_prob"] = 0.523
        df_final.loc[no_mask, "data_type"] = "🛰️ Professional Intelligence Feed"
        
        df_final["ev"] = df_final.apply(lambda r: calculate_ev(r["model_prob"], r["decimal_odds"]), axis=1)
        df_final["ss_ev"] = df_final.apply(lambda r: calculate_sport_select_ev(r["model_prob"], r["decimal_odds"], reduction_factor), axis=1)
        
        df_final["kelly_stake"] = df_final.apply(lambda r: kelly_criterion(r["model_prob"], r["decimal_odds"], fractional_kelly) * bankroll, axis=1)
        cap = bankroll * MAX_STAKE_CAP
        df_final["kelly_stake"] = df_final["kelly_stake"].clip(lower=0, upper=cap)
        df_final["potential_profit"] = df_final["kelly_stake"] * (df_final["decimal_odds"] - 1.0)
        
        def calculate_upset_score(r):
            if r["data_type"] == "💎 Multi-Source Alpha Yield": 
                return r["model_prob"] - r["implied_prob"]
            return (1000 / (abs(r["team_elo"] - r["opp_elo"]) + 1)) * r["model_prob"]
        
        df_final["upset_score"] = df_final.apply(calculate_upset_score, axis=1)
        
    if status_callback: status_callback("✅ Synchronization Complete")
    
    return df_final, live_scores, df_standings, df_leaders

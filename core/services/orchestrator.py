import pandas as pd
from datetime import datetime, timedelta
from core.logger import terminal_logger as logger
import core.unified_config as config
from core.data_fetcher import get_mlb_schedule, get_rapid_odds, process_rapid_odds, get_tank01_scores
from core.stats_engine import get_2026_standings, get_2026_leaders, get_pitcher_stats, get_team_hitting_stats
from core.elo_ratings import normalize_team_name
from core.models import calculate_implied_probability, american_to_decimal, calculate_ev, calculate_sport_select_ev, kelly_criterion
from core.repositories.game_repository import get_game_repository
from core.repositories.elo_repository import get_elo_repository
from core.services.prediction_service import get_prediction_service
from core.scraper_engine import MLBScraper

def sync_mlb_data(bankroll, fractional_kelly, reduction_factor, status_callback=None):
    """Institutional Data Orchestrator (Phase 16)."""
    if status_callback: status_callback("📡 Initializing MLB Data Stream...")
    
    t = datetime.now()
    cur_date = t.strftime("%Y-%m-%d")
    nxt_date = (t + timedelta(days=1)).strftime("%Y-%m-%d")
    prev_date = (t - timedelta(days=3)).strftime("%Y-%m-%d")
    
    # 1. 📡 Sched & Odds Hydration
    if status_callback: status_callback("🛰️ Syncing Daily Slate (2026)...")
    full_sched = get_mlb_schedule(cur_date) + get_mlb_schedule(nxt_date)
    if not full_sched:
        logger.warning(f"No games found for {cur_date}-{nxt_date}")
        return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame()
        
    df_sched = pd.DataFrame(full_sched)
    df_sched["h_norm"] = df_sched["home_team"].apply(normalize_team_name)
    df_sched["a_norm"] = df_sched["away_team"].apply(normalize_team_name)
    
    # 2. 📡 Market Odds Sync (RapidAPI)
    raw_odds = get_rapid_odds(t.strftime("%Y%m%d"))
    df_odds = process_rapid_odds(raw_odds) if raw_odds["data"] else pd.DataFrame()
    
    # 3. 📉 Base Layer Hydration (Standings/Stats/Elo)
    if status_callback: status_callback("📊 Hydrating Institutional Intelligence...")
    standings = get_2026_standings()
    leaders = get_2026_leaders()
    live_scores = get_tank01_scores(t.strftime("%Y%m%d")).get("body", {}) if get_tank01_scores else {}
    
    # 4. 🧬 Repository & Service Layer Initializations
    game_repo = get_game_repository()
    elo_repo = get_elo_repository(standings)
    scraper = MLBScraper()
    pred_service = get_prediction_service(elo_repo, game_repo, scraper)
    
    # 5. 🚀 Batch Predictive Processing
    if status_callback: status_callback("🧬 Running Monte Carlo & XGBoost v3.0 Slate Analysis...")
    # Add history for fatigue context
    hist_raw = get_mlb_schedule(start_date=prev_date, end_date=cur_date)
    df_hist = pd.DataFrame(hist_raw) if hist_raw else pd.DataFrame()
    
    # Process predictions for each game in the slate
    preds_list = []
    for _, row in df_sched.iterrows():
        try:
            preds_list.append(pred_service.predict_matchup(row, df_hist))
        except Exception as e:
            logger.error(f"Prediction Error for Game {row.get('game_id')}: {e}")
            preds_list.append({}) 
            
    df_preds = pd.DataFrame(preds_list)
    df_full = pd.concat([df_sched.reset_index(drop=True), df_preds.reset_index(drop=True)], axis=1)
    
    # 6. 💰 Financial Alpha Hydration (Bankroll/Kelly/EV)
    if status_callback: status_callback("💰 Calculating Bankroll Staking & CLV Alpha...")
    final_payload = []
    
    for _, g in df_full.iterrows():
        # Match with Market Odds
        if not df_odds.empty:
            match = df_odds[(df_odds["home_team"].apply(normalize_team_name) == g["h_norm"]) & 
                            (df_odds["away_team"].apply(normalize_team_name) == g["a_norm"])]
            if not match.empty:
                for _, o in match.iterrows():
                    nr = g.to_dict()
                    nr.update({"bookmaker": o["bookmaker"], "outcome": o["outcome"], "odds": o["odds"], "market": o["market"]})
                    
                    is_home = (normalize_team_name(o["outcome"]) == g["h_norm"])
                    nr["model_prob"] = g["home_win_prob"] if is_home else g["away_win_prob"]
                    nr["team_elo_adj"] = g["home_elo_adj"] if is_home else g["away_elo_adj"]
                    nr["opp_elo_adj"] = g["away_elo_adj"] if is_home else g["home_elo_adj"]
                    nr["team_proj"] = g["home_proj"] if is_home else g["away_proj"]
                    nr["opp_proj"] = g["away_proj"] if is_home else g["home_proj"]
                    final_payload.append(nr)
                continue
        
        # Fallback if no odds present for game
        nr = g.to_dict()
        nr.update({"bookmaker": "Pending", "outcome": g["home_team"], "odds": None, "market": "h2h", 
                   "model_prob": g["home_win_prob"], "team_elo_adj": g["home_elo_adj"], 
                   "opp_elo_adj": g["away_elo_adj"], "team_proj": g["home_proj"], "opp_proj": g["away_proj"]})
        final_payload.append(nr)
        
    df_f = pd.DataFrame(final_payload)
    if not df_f.empty:
        df_f["implied_prob"] = df_f["odds"].apply(calculate_implied_probability) if "odds" in df_f else 0.5
        df_f["decimal_odds"] = df_f["odds"].apply(american_to_decimal) if "odds" in df_f else 1.91
        df_f["ev"] = df_f.apply(lambda r: calculate_ev(r["model_prob"], r["decimal_odds"]), axis=1)
        df_f["ss_ev"] = df_f.apply(lambda r: calculate_sport_select_ev(r["model_prob"], r["decimal_odds"], reduction_factor), axis=1)
        df_f["kelly_stake"] = df_f.apply(lambda r: kelly_criterion(r["model_prob"], r["decimal_odds"], fractional_kelly) * bankroll, axis=1)
        
        # Strategy Hardening
        cap = bankroll * config.MAX_STAKE_CAP
        df_f["kelly_stake"] = df_f["kelly_stake"].clip(lower=0, upper=cap)
        df_f["potential_profit"] = df_f["kelly_stake"] * (df_f["decimal_odds"] - 1.0)
        
        # Formatting for UI
        df_f["formatted_time"] = pd.to_datetime(df_f["commence_time"]).dt.strftime("%a, %b %d @ %I:%M %p")
        df_f["upset_score"] = df_f.apply(lambda r: (r["model_prob"] - r["implied_prob"]) * 100, axis=1)
        
    return df_f, live_scores, standings, leaders

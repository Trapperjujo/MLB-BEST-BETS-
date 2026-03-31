import pandas as pd
from datetime import datetime, timedelta
from core.database import terminal_db
from core.logger import terminal_logger as logger
from core.scraper_engine import MLBScraper
from core.data_fetcher import get_mlb_schedule, get_rapid_odds, get_tank01_scores
from core.stats_engine import get_2026_standings, get_2026_leaders
from core.elo_ratings import normalize_team_name
from core.models import american_to_decimal, calculate_ev, kelly_criterion
from core.services.prediction_service import get_prediction_service
from core.services.game_repository import get_game_repository
from core.services.elo_repository import get_elo_repository

def sync_mlb_data(bankroll, fractional_kelly, reduction_factor, std_bet_size=1.0, status_callback=None):
    """
    💎 Unified Orchestrator: Triple-Source Synchronization (Phase 17).
    Primary: API | Secondary: Scraper Alpha | Tertiary: DuckDB Cache | Layer 0: Local Persistence
    """
    from core.data_fetcher import save_sync_cache, load_sync_cache
    sync_status = "💎 ACTIVE" # Default
    
    try:
        if status_callback: status_callback("📡 Initializing Triple-Source Sync...")
        
        t = datetime.now()
        cur_date = t.strftime("%Y-%m-%d")
        date_path = t.strftime("%Y%m%d")
        
        # 1. 💎 LAYER 1: Primary API Sync (Odds & Slate)
        if status_callback: status_callback("🛰️ Syncing Layer 1: Primary API Slate...")
        full_sched = get_mlb_schedule(cur_date)
        
        if not full_sched:
            logger.warning("Primary Sync Failed: Schedule empty. Attempting Layer 0 Cache Fallback.")
            lkg_cache = load_sync_cache()
            if lkg_cache:
                return pd.DataFrame(lkg_cache.get("df_f", [])), lkg_cache.get("live_scores", {}), pd.DataFrame(lkg_cache.get("standings", [])), pd.DataFrame(lkg_cache.get("leaders", [])), "⚠️ CACHE_FAILOVER"
            return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), "🔴 SYNC_OFFLINE"
        
        df_sched = pd.DataFrame(full_sched)
        df_sched["h_norm"] = df_sched["home_team"].apply(normalize_team_name)
        df_sched["a_norm"] = df_sched["away_team"].apply(normalize_team_name)
        
        # Unified Odds Fetch (Multi-Booking Layer)
        odds_payload = get_rapid_odds(date_path)
        df_odds = pd.DataFrame(odds_payload["data"]) if odds_payload["data"] else pd.DataFrame()
        sync_source = odds_payload["source"]
        
        # 2. 🛰️ LAYER 2: Secondary Scraper Sync (Glossary Alpha)
        if status_callback: status_callback("🧬 Syncing Layer 2: Institutional Glossary Alpha...")
        scraper = MLBScraper()
        glossary_data = scraper.scrape_comprehensive_glossary_alpha(2026)
        
        # 🏛️ NEW: LAYER 4: Official MLB Ground Truth Sync
        if status_callback: status_callback("🏛️ Syncing Layer 4: Official MLB Ground Truth...")
        official_data = scraper.scrape_mlb_official_standings(2026)
        if official_data:
            terminal_db.upsert_official_standings(official_data)
        
        # 3. 💾 LAYER 3: Tertiary Cache Sync (DuckDB Persistence)
        if glossary_data:
            if status_callback: status_callback("💾 Syncing Layer 3: DuckDB Persistence...")
            for aspect in ["batting", "pitching", "fielding"]:
                terminal_db.upsert_team_metrics(aspect, glossary_data.get(aspect, []))
                
        # 4. 📉 Intelligence Hydration
        standings = get_2026_standings()
        leaders = get_2026_leaders()
        live_scores = get_tank01_scores(date_path).get("body", {})
        
        # 5. 🚀 Batch Predictive Execution
        game_repo = get_game_repository()
        elo_repo = get_elo_repository(standings)
        pred_service = get_prediction_service(elo_repo, game_repo, scraper)
        
        prev_date = (t - timedelta(days=3)).strftime("%Y-%m-%d")
        hist_raw = get_mlb_schedule(start_date=prev_date, end_date=cur_date)
        df_hist = pd.DataFrame(hist_raw) if hist_raw else pd.DataFrame()
        
        preds_list = []
        for _, row in df_sched.iterrows():
            try:
                # Prediction Service now utilizes the 130+ metric DuckDB layer
                preds_list.append(pred_service.predict_matchup(row, df_hist))
            except Exception as e:
                logger.error(f"Sync Error: {e}")
                preds_list.append({
                    'home_team': normalize_team_name(row["home_team"]),
                    'away_team': normalize_team_name(row["away_team"]),
                    'home_win_prob': 0.5, 'away_win_prob': 0.5, 
                    'home_elo': 1500, 'away_elo': 1500,
                    'home_proj': 4.5, 'away_proj': 4.5,
                    'xg_prob': 0.5, 'xg_conf': 0.0,
                    'h_p_era': 4.5, 'a_p_era': 4.5,
                    'home_scores_sample': [4,5,4,5], 'away_scores_sample': [4,5,4,5]
                })
                
        df_preds = pd.DataFrame(preds_list)
        df_full = pd.concat([df_sched.reset_index(drop=True), df_preds.reset_index(drop=True)], axis=1)
        
        # 6. Final Payload Formatting
        final_payload = []
        for _, g in df_full.iterrows():
            match_found = False
            if not df_odds.empty:
                # Match standardized Tank01/OddsAPI outputs
                m = df_odds[(df_odds["home_team"].apply(normalize_team_name) == g["h_norm"]) & 
                           (df_odds["away_team"].apply(normalize_team_name) == g["a_norm"])]
                if not m.empty:
                    # 💎 Institutional Market Metrics
                    market_avg = m["odds"].mean()
                    sharp_m = m[m["is_sharp"] == True]
                    sharp_benchmark = sharp_m["odds"].mean() if not sharp_m.empty else None
                    sources_count = m["bookmaker"].nunique()
                    
                    for _, o in m.iterrows():
                        nr = g.to_dict()
                        nr.update({
                            "bookmaker": o["bookmaker"], 
                            "outcome": o["outcome"], 
                            "odds": o["odds"], 
                            "market": o["market"], 
                            "data_source": sync_source,
                            "market_avg": market_avg,
                            "sharp_benchmark": sharp_benchmark,
                            "sources_count": sources_count
                        })
                        is_h = (normalize_team_name(o["outcome"]) == g["h_norm"])
                        nr["model_prob"] = g["home_win_prob"] if is_h else g["away_win_prob"]
                        final_payload.append(nr)
                    match_found = True
            
            if not match_found:
                nr = g.to_dict()
                nr.update({"bookmaker": "Pending", "outcome": g["home_team"], "odds": None, "market": "h2h", "data_source": "🛰️ Scraper Fallback"})
                nr["model_prob"] = g.get("home_win_prob", 0.5)
                final_payload.append(nr)
                
        import numpy as np
        
        df_f = pd.DataFrame(final_payload)
        if not df_f.empty:
            # 💎 Vault Mode: Pre-compute Chart Distributions for 100% Stability
            df_f["a_p25"] = df_f["away_scores_sample"].apply(lambda x: np.percentile(x, 25) if isinstance(x, list) else 0)
            df_f["a_p50"] = df_f["away_scores_sample"].apply(lambda x: np.percentile(x, 50) if isinstance(x, list) else 0)
            df_f["a_p75"] = df_f["away_scores_sample"].apply(lambda x: np.percentile(x, 75) if isinstance(x, list) else 0)
            df_f["h_p25"] = df_f["home_scores_sample"].apply(lambda x: np.percentile(x, 25) if isinstance(x, list) else 0)
            df_f["h_p50"] = df_f["home_scores_sample"].apply(lambda x: np.percentile(x, 50) if isinstance(x, list) else 0)
            df_f["h_p75"] = df_f["home_scores_sample"].apply(lambda x: np.percentile(x, 75) if isinstance(x, list) else 0)
            
            df_f["ev"] = df_f.apply(lambda r: calculate_ev(r["model_prob"], american_to_decimal(r["odds"])) if r["odds"] else 0, axis=1)
            df_f["kelly_stake"] = df_f.apply(lambda r: kelly_criterion(r["model_prob"], american_to_decimal(r["odds"]), fractional_kelly) * bankroll if r["odds"] else 0, axis=1)
            df_f["formatted_time"] = pd.to_datetime(df_f["commence_time"]).dt.strftime("%a, %b %d @ %I:%M %p")
        
        # 💾 Persistence: Save successful sync to Layer 0
        save_sync_cache({
            "df_f": df_f.to_dict(orient='records'),
            "live_scores": live_scores,
            "standings": standings.to_dict(orient='records') if hasattr(standings, 'to_dict') else standings,
            "leaders": leaders.to_dict(orient='records') if hasattr(leaders, 'to_dict') else leaders
        })
        
        return df_f, live_scores, standings, leaders, sync_status

    except Exception as e:
        logger.error(f"Global Sync Error: {e}")
        lkg_cache = load_sync_cache()
        if lkg_cache:
            return pd.DataFrame(lkg_cache.get("df_f", [])), lkg_cache.get("live_scores", {}), pd.DataFrame(lkg_cache.get("standings", [])), pd.DataFrame(lkg_cache.get("leaders", [])), "⚠️ CACHE_FAILOVER"
        return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), "🔴 SYNC_OFFLINE"
    
def get_sync_status_color(status: str) -> str:
    """Returns the CSS color for the sync status indicator."""
    if "ACTIVE" in status: return "#39ff14"
    if "CACHE" in status: return "#ffcc00"
    return "#ff4b4b"

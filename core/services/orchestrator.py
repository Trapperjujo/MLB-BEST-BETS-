from core.database import terminal_db

def sync_mlb_data(bankroll, fractional_kelly, reduction_factor, status_callback=None):
    """
    💎 Unified Orchestrator: Triple-Source Synchronization (Phase 17).
    Primary: API | Secondary: Scraper Alpha | Tertiary: DuckDB Cache
    """
    if status_callback: status_callback("📡 Initializing Triple-Source Sync...")
    
    t = datetime.now()
    cur_date = t.strftime("%Y-%m-%d")
    date_path = t.strftime("%Y%m%d")
    
    # 1. 💎 LAYER 1: Primary API Sync (Odds & Slate)
    if status_callback: status_callback("🛰️ Syncing Layer 1: Primary API Slate...")
    full_sched = get_mlb_schedule(cur_date)
    if not full_sched:
        logger.warning("Primary Sync Failed: Schedule empty. Checking Tertiary Cache.")
        # Fallback logic here if needed
        return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame()
        
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
            preds_list.append({'home_win_prob': 0.5, 'away_win_prob': 0.5, 'home_proj': 4.5})
            
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
                for _, o in m.iterrows():
                    nr = g.to_dict()
                    nr.update({"bookmaker": o["bookmaker"], "outcome": o["outcome"], "odds": o["odds"], "market": o["market"], "data_source": sync_source})
                    is_h = (normalize_team_name(o["outcome"]) == g["h_norm"])
                    nr["model_prob"] = g["home_win_prob"] if is_h else g["away_win_prob"]
                    final_payload.append(nr)
                match_found = True
        
        if not match_found:
            nr = g.to_dict()
            nr.update({"bookmaker": "Pending", "outcome": g["home_team"], "odds": None, "market": "h2h", "data_source": "🛰️ Scraper Fallback"})
            nr["model_prob"] = g.get("home_win_prob", 0.5)
            final_payload.append(nr)
            
    df_f = pd.DataFrame(final_payload)
    if not df_f.empty:
        df_f["ev"] = df_f.apply(lambda r: calculate_ev(r["model_prob"], american_to_decimal(r["odds"])) if r["odds"] else 0, axis=1)
        df_f["kelly_stake"] = df_f.apply(lambda r: kelly_criterion(r["model_prob"], american_to_decimal(r["odds"]), fractional_kelly) * bankroll if r["odds"] else 0, axis=1)
        df_f["formatted_time"] = pd.to_datetime(df_f["commence_time"]).dt.strftime("%a, %b %d @ %I:%M %p")
        
    return df_f, live_scores, standings, leaders

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict
import os
import sys

# Ensure the app root is in the python path for modular imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import json
from dotenv import load_dotenv
from core.config import CURRENT_SEASON, BANKROLL_DEFAULT, STD_BET_SIZE_DEFAULT, MIN_EDGE_DEFAULT, FRACTIONAL_KELLY, MAX_STAKE_CAP, KELLY_MODES, DEFAULT_KELLY_MODE, CAD_USD_XRATE
from core.data_fetcher import get_mlb_odds, process_odds_data, get_mlb_schedule
from core.models import american_to_decimal, calculate_ev, calculate_implied_probability, flat_staking, kelly_criterion, calculate_elo_probability, calculate_sport_select_ev, calculate_expected_runs, calculate_war_elo_adjustment, run_monte_carlo_simulation
from core.strategy import is_divisional_matchup
from core.elo_ratings import get_team_elo, load_elo_ratings, normalize_team_name
from core.status_fetcher import get_player_injuries, get_fatigue_penalty
from core.stats_engine import get_2026_standings, get_2026_leaders
from core.prediction_xgboost import predict_xgboost
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Neon Colors for Charts
var_neon_green = "#39ff14"
var_neon_blue = "#00f3ff"

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Configuration
st.set_page_config(page_title="BEST BETS | MLB Analytics", page_icon="⚾", layout="wide")

# Load CSS
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/main.css")
load_css("styles/neon_theme.css")

# Hero Section
if os.path.exists("hero.png"):
    st.image("hero.png", use_container_width=True)

# App Title
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 5px; letter-spacing: -2px;'>BEST BETS</h1>
        <p style='color: #94a3b8; font-size: 1.4rem; font-weight: 300;'>Professional MLB Predictive Terminal</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("### 🛠️ Risk Management")
bankroll = st.sidebar.number_input("Total Bankroll (CAD)", min_value=100.0, value=BANKROLL_DEFAULT, step=100.0)
kelly_mode = st.sidebar.selectbox("Kelly Criterion Mode", list(KELLY_MODES.keys()), index=list(KELLY_MODES.keys()).index(DEFAULT_KELLY_MODE))
fractional_kelly = KELLY_MODES[kelly_mode]

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Engine Settings")
std_bet_size = st.sidebar.slider("Standard Bet Size (%)", 0.5, 5.0, STD_BET_SIZE_DEFAULT, 0.1, help="The percentage of your total bankroll you consider one 'unit'.")
min_edge = st.sidebar.slider("Minimum Edge Needed (%)", 0.0, 10.0, MIN_EDGE_DEFAULT, 0.5) / 100
cad_rate = st.sidebar.number_input("CAD/USD Rate", value=CAD_USD_XRATE, step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Navigation")
page = st.sidebar.radio("View Mode", ["🎯 Intelligence Feed", "🗓️ Full Predictions", "📈 2026 Standings", "🏆 Team Power Rankings", "🧬 Player Analytics"])

if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Dashboard Sorting")
sort_mode = st.sidebar.selectbox("Sort Predictions By", [
    "🔥 Highest +EV", 
    "🏆 Most Likely to Win", 
    "⚡ Likely Upset"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Strategies")
enable_ss_mode = st.sidebar.toggle("🇨🇦 Sport Select Optimizer", value=False)
reduction_factor = st.sidebar.slider("SS Reduction Factor", 0.70, 0.95, 0.91, 0.01) if enable_ss_mode else 0.91

# WAR Data Loading
@st.cache_data
def load_team_war_map():
    path = "data/raw/player_war_2024.csv"
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    # Simplify Team mapping for WAR (e.g., NYY -> New York Yankees)
    from core.elo_ratings import ABBR_MAP
    # Reverse map ABBRs to full names
    # Note: Some teams in CSV might be abbrs
    team_war = df.groupby('Team')['WAR'].sum().to_dict()
    full_team_war = {}
    for team, war in team_war.items():
        full_name = ABBR_MAP.get(team, team)
        full_team_war[full_name] = war
    return full_team_war

team_war_map = load_team_war_map()

# Elo Calculations Logic
def get_prediction(row, history_df: pd.DataFrame = None):
    h_team = normalize_team_name(row["home_team"])
    a_team = normalize_team_name(row["away_team"])
    h_elo = get_team_elo(h_team)
    a_elo = get_team_elo(a_team)
    
    # Fatigue check
    h_fatigue = get_fatigue_penalty(h_team, history_df)
    a_fatigue = get_fatigue_penalty(a_team, history_df)
    
    # WAR Adjustment
    h_war = team_war_map.get(h_team, 0.0)
    a_war = team_war_map.get(a_team, 0.0)
    war_diff_adj = calculate_war_elo_adjustment(h_war, a_war)
    
    # RUN MONTE CARLO
    mc_results = run_monte_carlo_simulation(
        home_elo=int(h_elo), 
        away_elo=int(a_elo), 
        adjustments={'home': -h_fatigue, 'away': -a_fatigue, 'lineup_war_diff': war_diff_adj}
    )
    
    # RUN XGBOOST
    xg_prob, xg_conf = predict_xgboost(h_team, a_team)
    
    return {
        'home_win_prob': mc_results['home_win_prob'],
        'away_win_prob': mc_results['away_win_prob'],
        'home_elo': h_elo,
        'away_elo': a_elo,
        'home_proj': mc_results['home_avg_runs'],
        'away_proj': mc_results['away_avg_runs'],
        'home_scores_sample': mc_results['home_scores'],
        'away_scores_sample': mc_results['away_scores'],
        'xg_prob': xg_prob,
        'xg_conf': xg_conf
    }

# Data Fetching
@st.cache_data(ttl=600)
def fetch_master_data():
    with st.status("📡 Initializing MLB Data Stream...", expanded=True) as status:
        # 1. Fetch Schedule (Today + Tomorrow)
        today_dt = datetime.now()
        today = today_dt.strftime("%Y-%m-%d")
        tomorrow = (today_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        history_start = (today_dt - timedelta(days=3)).strftime("%Y-%m-%d")
        
        status.write("📅 Loading Schedule...")
        sched_today = get_mlb_schedule(today)
        sched_tomorrow = get_mlb_schedule(tomorrow)
        full_sched = sched_today + sched_tomorrow
        
        if not full_sched:
            status.update(label="⚠️ No games found for today.", state="error")
            return pd.DataFrame()
            
        df_sched = pd.DataFrame(full_sched)
        
        # 2. Historical Fatigue Lookups (Accelerated)
        status.write("⚡ Analyzing Team Fatigue (Last 3 Days)...")
        hist_raw = get_mlb_schedule(start_date=history_start, end_date=today)
        df_hist = pd.DataFrame(hist_raw) if hist_raw else pd.DataFrame()
        
        # 3. Fetch Odds (All Regions)
        status.write("💰 Syncing Global Betting Markets...")
        raw_odds = get_mlb_odds(regions="us,uk,eu,au")
        df_odds = process_odds_data(raw_odds) if raw_odds else pd.DataFrame()
        
        # 4. Build Predictions
        status.write("🤖 Running MLB Monte Carlo & XGBoost Hybrid Core...")
        df_sched["h_norm"] = df_sched["home_team"].apply(normalize_team_name)
        df_sched["a_norm"] = df_sched["away_team"].apply(normalize_team_name)
        
        predictions = df_sched.apply(lambda r: pd.Series(get_prediction(r, df_hist)), axis=1)
        df_sched = pd.concat([df_sched, predictions], axis=1)
        
        # 5. Fetch 2026 Standings
        status.write("📈 Fetching Live 2026 Standings & ATS Records...")
        df_standings = get_2026_standings()
        
        status.update(label="✅ Synchronization Complete", state="complete")
    
    final_rows = []
    
    # Store standings globally in state for UI
    st.session_state["df_standings_2026"] = df_standings
    st.session_state["df_leaders_2026"] = get_2026_leaders()
    
    for _, game in df_sched.iterrows():
        # Find matching odds
        if not df_odds.empty:
            match = df_odds[
                (df_odds["home_team"].apply(normalize_team_name) == game["h_norm"]) & 
                (df_odds["away_team"].apply(normalize_team_name) == game["a_norm"])
            ]
            
            if not match.empty:
                for _, odd_row in match.iterrows():
                    new_row = game.to_dict()
                    new_row.update({
                        "bookmaker": odd_row["bookmaker"],
                        "outcome": odd_row["outcome"],
                        "odds": odd_row["odds"],
                        "market": odd_row["market"]
                    })
                    # Use specific outcome probability
                    is_home = (normalize_team_name(odd_row["outcome"]) == game["h_norm"])
                    new_row["model_prob"] = game["home_win_prob"] if is_home else game["away_win_prob"]
                    new_row["team_elo"] = game["home_elo"] if is_home else game["away_elo"]
                    new_row["opp_elo"] = game["away_elo"] if is_home else game["home_elo"]
                    new_row["team_proj"] = game["home_proj"] if is_home else game["away_proj"]
                    new_row["opp_proj"] = game["away_proj"] if is_home else game["home_proj"]
                    final_rows.append(new_row)
                continue
        
        # If no odds found, add a placeholder row for "Full Predictions" tab
        new_row = game.to_dict()
        new_row.update({
            "bookmaker": "Pending", "outcome": game["home_team"], "odds": None, "market": "h2h",
            "model_prob": game["home_win_prob"], "team_elo": game["home_elo"], "opp_elo": game["away_elo"],
            "team_proj": game["home_proj"], "opp_proj": game["away_proj"]
        })
        final_rows.append(new_row)
        
    df_final = pd.DataFrame(final_rows)
    
    # Calculate Metrics
    if not df_final.empty:
        df_final["is_divisional"] = df_final.apply(lambda row: is_divisional_matchup(row["home_team"], row["away_team"]), axis=1)
        df_final["formatted_time"] = pd.to_datetime(df_final["commence_time"]).dt.strftime("%b %d, %H:%M")
        
        # Numeric calculations
        has_odds = df_final["odds"].notnull()
        
        # 1. Real Market Data
        df_final.loc[has_odds, "implied_prob"] = df_final.loc[has_odds, "odds"].apply(calculate_implied_probability)
        df_final.loc[has_odds, "decimal_odds"] = df_final.loc[has_odds, "odds"].apply(american_to_decimal)
        df_final.loc[has_odds, "data_type"] = "💎 Market Alpha"
        
        # 2. Simulated Mode (Theoretical -110 lines for sorting/edge analysis)
        no_odds = df_final["odds"].isnull()
        df_final.loc[no_odds, "decimal_odds"] = 1.91 # Theoretical -110
        df_final.loc[no_odds, "implied_prob"] = 0.523 # 1/1.91
        df_final.loc[no_odds, "data_type"] = "🧪 Simulation Mode"
        
        # Common Calculations
        df_final["ev"] = df_final.apply(lambda row: calculate_ev(row["model_prob"], row["decimal_odds"]), axis=1)
        df_final["ss_ev"] = df_final.apply(lambda row: calculate_sport_select_ev(row["model_prob"], row["decimal_odds"], reduction_factor), axis=1)
        
        # Kelly only for real odds or for high-confidence simulations
        df_final.loc[has_odds, "kelly_stake"] = df_final[has_odds].apply(lambda row: kelly_criterion(row["model_prob"], row["decimal_odds"], fractional_kelly) * bankroll, axis=1)
        
        # Apply Max Stake Cap (3% as per Qwen strategy)
        cap_val = bankroll * MAX_STAKE_CAP
        df_final.loc[has_odds, "kelly_stake"] = df_final.loc[has_odds, "kelly_stake"].clip(upper=cap_val)
        
        df_final.loc[has_odds, "potential_profit"] = df_final["kelly_stake"] * (df_final["decimal_odds"] - 1.0)
        
        # Upset Score: High model prob for teams with low implied prob (underdogs)
        # For simulation mode (no odds), we use Elo proximity as proxy
        def calc_upset_score(row):
            if row["data_type"] == "💎 Market Alpha":
                # Higher score if model_prob is high but implied_prob is low
                return row["model_prob"] - row["implied_prob"]
            else:
                # Simulation proxy: Narrow Elo gap (high tension)
                elo_diff = abs(row["team_elo"] - row["opp_elo"])
                return (1000 / (elo_diff + 1)) * row["model_prob"]
                
        df_final["upset_score"] = df_final.apply(calc_upset_score, axis=1)
        
    return df_final

# Execution
df_master = fetch_master_data()

if df_master.empty:
    st.error("Critical Error: Unable to fetch MLB Schedule or Market Data. Check your API connections.")
    st.stop()

# Update counts dynamically
ev_count = len(df_master[(df_master["odds"].notnull()) & (df_master["ev"] >= min_edge)])
total_count = len(df_master.drop_duplicates(subset=["game_id"]))

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📡 Sync Status:** {total_count} Games Active")
st.sidebar.markdown(f"**🎯 Value Alerts:** {ev_count} detected")

# FIX: Main Dashboard Header
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bankroll", f"${bankroll:,.2f} CAD")
with col2:
    st.metric("Base Unit (1.0u)", f"${flat_staking(bankroll, std_bet_size):,.2f}")
with col3:
    st.metric("Model Fidelity", "Elo + 4 Regions", delta="High")
with col4:
    st.metric("Active Regions", "US, UK, EU, AU", delta="Linked")

st.markdown("---")

# Main Dashboard Routing (Unified Feed)
st.subheader(f"⚾ MLB Predictions Master Feed ({total_count} Games)")

# Sort the master view to favor best bets
df_master = df_master.sort_values(by="ev", ascending=False)
df_sched_view = df_master.drop_duplicates(subset=["game_id"])

if sort_mode == "🔥 Highest +EV":
    df_sched_view = df_sched_view.sort_values(by="ev", ascending=False)
elif sort_mode == "🏆 Most Likely to Win":
    df_sched_view["max_prob"] = df_sched_view[["home_win_prob", "away_win_prob"]].max(axis=1)
    df_sched_view = df_sched_view.sort_values(by="max_prob", ascending=False)
else:
    df_sched_view = df_sched_view.sort_values(by="upset_score", ascending=False)

st.info(f"📊 Displaying all predictions. Sorted by: {sort_mode}. Simulation Mode (Grey) uses -110 market defaults.")

# Iterate and display cards
for idx, row in df_sched_view.iterrows():
    game_bets = df_master[df_master["game_id"] == row["game_id"]]
    best_bet = game_bets.sort_values(by="ev", ascending=False).iloc[0] if not game_bets.empty else row
    
    display_date = pd.to_datetime(row["commence_time"]).strftime("%a, %b %d") if not isinstance(row["commence_time"], pd.Series) else pd.to_datetime(row["commence_time"].iloc[0]).strftime("%a, %b %d")
    
    with st.container():
        # Retrieve 2026 Standings for the teams
        df_s = st.session_state.get("df_standings_2026", pd.DataFrame())
        h_rec = df_s[df_s["Team"] == row["home_team"]].iloc[0] if not df_s.empty and not df_s[df_s["Team"] == row["home_team"]].empty else None
        a_rec = df_s[df_s["Team"] == row["away_team"]].iloc[0] if not df_s.empty and not df_s[df_s["Team"] == row["away_team"]].empty else None
        
        h_rec_str = f"{h_rec['W']}-{h_rec['L']} ({h_rec['ATS_W']}-{h_rec['ATS_L']} ATS)" if h_rec is not None else "0-0 (0-0 ATS)"
        a_rec_str = f"{a_rec['W']}-{a_rec['L']} ({a_rec['ATS_W']}-{a_rec['ATS_L']} ATS)" if a_rec is not None else "0-0 (0-0 ATS)"

        # XGBoost Synergy Check
        synergy_badge = ""
        if (row['home_win_prob'] > 0.5 and row['xg_prob'] > 0.5) or (row['home_win_prob'] < 0.5 and row['xg_prob'] < 0.5):
            synergy_badge = f"<span class='synergy-badge'>⚡ XGBoost Synergy: {row['xg_conf']*100:.0f}%</span>"

        # Build the HTML string for the card
        card_html = f"""
<div class='neon-card'>
<div class='neon-card-header'>
<div style='display: flex; align-items: center; gap: 10px;'>
<span style='font-size: 1.2rem;'>📅 {display_date}</span>
<span class='alpha-badge'>{best_bet['data_type']}</span>
{synergy_badge}
</div>
{f"<div class='ev-badge'>+{best_bet['ev']*100:.1f}% EV</div>" if best_bet['ev'] > 0 else ""}
</div>
<div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center;'>
<div>
<div style='color: var(--text-secondary); font-size: 0.8rem;'>AWAY</div>
<div style='font-size: 1.1rem; font-weight: 700;'>{row['away_team']}</div>
<div style='font-size: 0.7rem; color: #94a3b8; margin-bottom: 5px;'>2026: {a_rec_str}</div>
<div style='color: var(--neon-green); font-size: 1.4rem; font-weight: 800;'>{row['away_win_prob']*100:.1f}%</div>
<div style='font-size: 0.9rem;'>Proj: {row['away_proj']:.1f} runs</div>
</div>
<div style='display: flex; flex-direction: column; justify-content: center; align-items: center;'>
<div style='font-size: 0.7rem; color: var(--text-secondary);'>PREDICTED WINNER</div>
<div style='font-size: 1.2rem; font-weight: 900; color: #fff;'>{row['home_team'] if row['home_win_prob'] > 0.5 else row['away_team']}</div>
<div style='font-size: 0.7rem; color: var(--neon-blue); margin-top: 5px;'>ML confidence: {row['xg_conf']*100:.0f}%</div>
</div>
<div>
<div style='color: var(--text-secondary); font-size: 0.8rem;'>HOME</div>
<div style='font-size: 1.1rem; font-weight: 700;'>{row['home_team']}</div>
<div style='font-size: 0.7rem; color: #94a3b8; margin-bottom: 5px;'>2026: {h_rec_str}</div>
<div style='color: var(--neon-green); font-size: 1.4rem; font-weight: 800;'>{row['home_win_prob']*100:.1f}%</div>
<div style='font-size: 0.9rem;'>Proj: {row['home_proj']:.1f} runs</div>
</div>
</div>
"""
        # Append Risk Guidance if applicable
        if best_bet["ev"] >= min_edge and best_bet["data_type"] == "💎 Market Alpha":
            card_html += f"""
<div style='margin-top: 20px; padding: 15px; background: rgba(57, 255, 20, 0.05); border-left: 4px solid var(--neon-green); border-radius: 4px;'>
<div style='display: flex; justify-content: space-between;'>
<div>
<div style='font-size: 0.7rem; color: var(--text-secondary);'>SUGGESTED WAGER ({kelly_mode})</div>
<div style='font-size: 1.3rem; font-weight: 800; color: var(--neon-green);'>${best_bet['kelly_stake']:,.2f} CAD</div>
</div>
<div style='text-align: right;'>
<div style='font-size: 0.7rem; color: var(--text-secondary);'>EST. PROFIT</div>
<div style='font-size: 1.3rem; font-weight: 800; color: #fff;'>+${best_bet['potential_profit']:,.2f}</div>
</div>
</div>
<div style='font-size: 0.7rem; color: var(--text-secondary); margin-top: 10px;'>
Target: {best_bet['outcome']} @ {best_bet['odds']} ({best_bet['bookmaker']})
</div>
</div>
"""
        
        # Close the neon-card div
        card_html += "</div>"
        
        # Render the full card
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Details view in expander
        with st.expander("🔍 Matchup Analysis & Market Depth"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Elo Spread:** {int(row['home_elo'])} vs {int(row['away_elo'])}")
                st.write(f"**Status:** {row['status']}")
            with c2:
                # Distribution chart using sample scores
                hist_df = pd.DataFrame({
                    'Away': row['away_scores_sample'],
                    'Home': row['home_scores_sample']
                })
                fig = px.histogram(hist_df, barmode='overlay', template='plotly_dark', color_discrete_sequence=[var_neon_blue, var_neon_green])
                st.plotly_chart(fig, use_container_width=True)
                
            game_odds = df_master[df_master["game_id"] == row["game_id"]]
            game_odds = game_odds[game_odds["odds"].notnull()]
            if not game_odds.empty:
                st.dataframe(game_odds[["bookmaker", "outcome", "odds", "ev", "implied_prob"]], use_container_width=True)

# Analytics Modules at the bottom
st.markdown("---")
st.subheader("📊 Global Analytics Modules")

tab1, tab2, tab3, tab4 = st.tabs(["🏆 Elo Rankings", "📈 2026 Standings", "🥇 League Leaders", "🧬 Player Analytics"])

with tab1:
    st.subheader("🏆 Global Leaderboard: Elo Point Scores")
    elo_map = load_elo_ratings()
    elo_df = pd.DataFrame(list(elo_map.items()), columns=['Team', 'Elo']).sort_values(by='Elo', ascending=False)
    st.dataframe(elo_df.reset_index(drop=True), use_container_width=True)
    fig = px.bar(elo_df, x='Elo', y='Team', orientation='h', color='Elo', text='Elo', color_continuous_scale='Viridis', template='plotly_dark')
    fig.update_layout(height=800, margin=dict(l=20, r=20, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📈 Official 2026 Division Standings & ATS Records")
    df_s_2026 = st.session_state.get("df_standings_2026", pd.DataFrame())
    if not df_s_2026.empty:
        st.dataframe(df_s_2026, use_container_width=True)
        fig_s = px.scatter(df_s_2026, x="W", y="ATS_W", text="Team", color="League", title="Wins vs Against-The-Spread Wins", template="plotly_dark")
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("2026 Standing data not fetched yet. Click 'Refresh' to sync.")

with tab3:
    st.subheader("🥇 2026 Seasonal League Leaders")
    leaders_map = st.session_state.get("df_leaders_2026", {})
    if leaders_map:
        l_tabs = st.tabs(["🔥 Home Runs", "🎯 Batting Avg", "⚾ ERA", "🏆 Wins"])
        with l_tabs[0]: st.table(leaders_map.get("homeRuns"))
        with l_tabs[1]: st.table(leaders_map.get("battingAverage"))
        with l_tabs[2]: st.table(leaders_map.get("earnedRunAverage"))
        with l_tabs[3]: st.table(leaders_map.get("wins"))
    else:
        st.info("Leaderboard data currently unavailable.")

with tab4:
    st.subheader("🧬 Player Analytics (Baseline WAR)")
    if os.path.exists("data/raw/player_war_2024.csv"):
        df_war = pd.read_csv("data/raw/player_war_2024.csv")
        fig_war = px.treemap(df_war, path=['Team', 'Name'], values='WAR', color='WAR', color_continuous_scale='RdYlGn', template='plotly_dark')
        st.plotly_chart(fig_war, use_container_width=True)
    else:
        st.info("Player WAR stats not found.")

st.markdown("---")
with st.expander("🔍 Market & Elo Depth (Raw Data)"):
    st.dataframe(df_master, use_container_width=True)

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 50px; opacity: 0.6;'>
        <p>© 2026 BEST BETS Analytics Engine. Data by MLB Stats API & The Odds API.</p>
        <p style='font-size: 0.8rem;'>Sports betting involves risk. Wager only what you can afford to lose.</p>
    </div>
""", unsafe_allow_html=True)

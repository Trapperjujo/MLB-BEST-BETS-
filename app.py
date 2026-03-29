import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from core.data_fetcher import get_mlb_odds, process_odds_data, get_mlb_schedule
from core.models import american_to_decimal, calculate_ev, calculate_implied_probability, flat_staking, kelly_criterion, calculate_elo_probability, calculate_sport_select_ev, calculate_expected_runs, calculate_war_elo_adjustment
from core.strategy import is_divisional_matchup
from core.elo_ratings import get_team_elo, load_elo_ratings, normalize_team_name
from core.status_fetcher import get_player_injuries, get_fatigue_penalty
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="BEST BETS | MLB Analytics", page_icon="⚾", layout="wide")

# Load CSS
if os.path.exists("styles/main.css"):
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
st.sidebar.markdown("### 🛠️ Configuration")
bankroll = st.sidebar.number_input("Total Bankroll (CAD)", min_value=100.0, value=5000.0, step=100.0)
std_bet_size = st.sidebar.slider("Standard Bet Size (%)", 0.5, 5.0, 1.5, 0.1, help="The percentage of your total bankroll you consider one 'unit'.")
min_edge = st.sidebar.slider("Minimum Edge Needed (%)", 0.0, 100.0, 3.0, 0.5, help="Filter for the Intelligence Feed.") / 100
fractional_kelly = st.sidebar.slider("Fractional Kelly multiplier", 0.1, 1.0, 0.25, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Navigation")
page = st.sidebar.radio("View Mode", ["🎯 Intelligence Feed", "🗓️ Full Predictions", "📈 Team Power Rankings", "🧬 Player WAR Analytics"])

if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Strategies")
enable_ss_mode = st.sidebar.toggle("🇨🇦 Sport Select Optimizer", value=False)
reduction_factor = st.sidebar.slider("SS Reduction Factor", 0.70, 0.95, 0.91, 0.01) if enable_ss_mode else 0.91

# Elo Calculations Logic
def get_prediction(row):
    h_team = normalize_team_name(row["home_team"])
    a_team = normalize_team_name(row["away_team"])
    h_elo = get_team_elo(h_team)
    a_elo = get_team_elo(a_team)
    
    h_fatigue = get_fatigue_penalty(h_team)
    a_fatigue = get_fatigue_penalty(a_team)
    
    adjustments = {'home': -h_fatigue, 'away': -a_fatigue, 'lineup_war_diff': 0.0}
    h_win_prob = calculate_elo_probability(h_elo, a_elo, adjustments=adjustments)
    
    h_proj = calculate_expected_runs(h_elo, a_elo)
    a_proj = calculate_expected_runs(a_elo, h_elo)
    
    # Return probabilities for both outcomes
    return {
        'home_win_prob': h_win_prob,
        'away_win_prob': 1.0 - h_win_prob,
        'home_elo': h_elo,
        'away_elo': a_elo,
        'home_proj': h_proj,
        'away_proj': a_proj
    }

# Data Fetching
@st.cache_data(ttl=600)
def fetch_master_data():
    # 1. Fetch Schedule (Today + Tomorrow)
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    sched_today = get_mlb_schedule(today)
    sched_tomorrow = get_mlb_schedule(tomorrow)
    full_sched = sched_today + sched_tomorrow
    
    if not full_sched:
        return pd.DataFrame()
        
    df_sched = pd.DataFrame(full_sched)
    
    # 2. Fetch Odds (All Regions)
    raw_odds = get_mlb_odds(regions="us,uk,eu,au")
    df_odds = process_odds_data(raw_odds) if raw_odds else pd.DataFrame()
    
    # 3. Merge Strategy
    # We want to attach odds to our schedule games.
    # Normalizing names for matching
    df_sched["h_norm"] = df_sched["home_team"].apply(normalize_team_name)
    df_sched["a_norm"] = df_sched["away_team"].apply(normalize_team_name)
    
    predictions = df_sched.apply(lambda r: pd.Series(get_prediction(r)), axis=1)
    df_sched = pd.concat([df_sched, predictions], axis=1)
    
    final_rows = []
    
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

with st.status("📡 Synchronizing MLB Schedule & Global Markets...", expanded=False) as status:
    df_master = fetch_master_data()
    status.update(label="✅ Dashboard Live", state="complete", expanded=False)

if df_master.empty:
    st.error("Critical Error: Unable to fetch MLB Schedule or Market Data. Check your API connections.")
    st.stop()
# Navigation Logic

# Update counts dynamically
ev_count = 0
total_count = 0
if not df_master.empty:
    ev_count = len(df_master[(df_master["odds"].notnull()) & (df_master["ev"] >= min_edge)])
    total_count = len(df_master.drop_duplicates(subset=["game_id"]))

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Navigation")
page = st.sidebar.radio("View Mode", [
    f"🗓️ Full Predictions ({total_count} Games)", 
    f"🎯 Intelligence Feed ({ev_count} Alerts)", 
    "📈 Team Power Rankings", 
    "🧬 Player WAR Analytics"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Dashboard Sorting")
sort_mode = st.sidebar.selectbox("Sort Predictions By", [
    "🔥 Highest +EV", 
    "🏆 Most Likely to Win", 
    "⚡ Likely Upset"
])

if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# FIX: Main Dashboard Header
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bankroll", f"${bankroll:,.2f} CAD")
with col2:
    st.metric("Base Unit (1.0u)", f"${flat_staking(bankroll, std_bet_size):,.2f}")
with col3:
    st.metric("Predictions Source", "MLB Stats API", delta="Live")
with col4:
    st.metric("Active Regions", "US, UK, EU, AU", delta="Active")

st.markdown("---")

# Navigation Routing
if page.startswith("🎯 Intelligence Feed"):
    st.subheader("🎯 Intelligence Feed: +EV Value Alerts")
    
    # Filter for games WITH odds and WITH edge
    df_value = df_master[df_master["odds"].notnull()]
    df_value = df_value[df_value["ev"] >= min_edge]
    
    # Sort based on global selector
    if sort_mode == "🔥 Highest +EV":
        df_value = df_value.sort_values(by="ev" if not enable_ss_mode else "ss_ev", ascending=False)
    elif sort_mode == "🏆 Most Likely to Win":
        df_value = df_value.sort_values(by="model_prob", ascending=False)
    else:
        df_value = df_value.sort_values(by="upset_score", ascending=False)

    if df_value.empty:
        st.info("No high-value opportunities detected. Try lowering 'Minimum Edge Needed' or check 'Full Predictions'.")
    else:
        for idx, row in df_value.iterrows():
            with st.container():
                strategy_pills = []
                if row['is_divisional']: strategy_pills.append("🏷️ Divisional Play")
                if (row['ss_ev' if enable_ss_mode else 'ev'] > 0.05): strategy_pills.append("🔥 High Value")
                
                pills_html = "".join([f"<span style='background: #6366f1; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; margin-right: 5px;'>{p}</span>" for p in strategy_pills])
                
                card_html = f"""<div class='bet-card'>
<div style='display: flex; justify-content: space-between; align-items: center;'>
<div>
<div style='color: #818cf8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; margin-bottom: 3px;'>🎯 Predicted Winner ({row['outcome']})</div>
<span style='font-size: 1.5rem; font-weight: 800; color: #fff; letter-spacing: -1px;'>{row['outcome']} {row['odds']}</span>
<div style='margin-top: 5px;'>{pills_html}</div>
</div>
<div style='text-align: right;'>
<div class='ev-badge'>+{row['ss_ev' if enable_ss_mode else 'ev']*100:.1f}% EV</div>
<div style='margin-top: 5px; font-size: 0.8rem; color: #64748b;'>{row['formatted_time']} • {row['bookmaker']}</div>
</div>
</div>
<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>
<div style='display: flex; justify-content: space-between; margin-bottom: 15px;'>
<div style='text-align: center; flex: 1;'>
<div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase;'>{row['away_team']}</div>
<div style='font-size: 1.3rem; font-weight: 700; color: #fff;'>{row['away_proj']:.1f}</div>
<div style='color: #94a3b8; font-size: 0.75rem;'>Elo: {int(row['away_elo'])}</div>
</div>
<div style='align-self: center; color: #475569; font-weight: 900; padding: 0 15px;'>VS</div>
<div style='text-align: center; flex: 1;'>
<div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase;'>{row['home_team']}</div>
<div style='font-size: 1.3rem; font-weight: 700; color: #fff;'>{row['home_proj']:.1f}</div>
<div style='color: #94a3b8; font-size: 0.75rem;'>Elo: {int(row['home_elo'])}</div>
</div>
</div>
<div style='margin-top: 15px; background: rgba(255, 255, 255, 0.02); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.03);'>
<div style='display: flex; justify-content: space-between;'>
<div>
<div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;'>Suggested Wager</div>
<div style='font-size: 1.25rem; color: #818cf8; font-weight: 700;'>${row['kelly_stake']:,.2f} CAD</div>
</div>
<div style='text-align: right;'>
<div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;'>Est. Profit</div>
<div style='font-size: 1.25rem; color: #10b981; font-weight: 700;'>+${row['potential_profit']:,.2f} CAD</div>
</div>
</div>
<div style='margin-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 10px; display: flex; justify-content: space-between;'>
<div style='color: #94a3b8; font-size: 0.85rem;'>Win Prob: <b>{row['model_prob']*100:.1f}%</b></div>
<div style='color: #94a3b8; font-size: 0.85rem;'>Starting: <b>{row['away_pitcher']} vs {row['home_pitcher']}</b></div>
</div>
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)

elif page.startswith("🗓️ Full Predictions"):
    st.subheader("🗓️ Full MLB Schedule & Elo Predictions")
    
    # Sort the master view
    df_sched_view = df_master.drop_duplicates(subset=["game_id"])
    
    if sort_mode == "🔥 Highest +EV":
        df_sched_view = df_sched_view.sort_values(by="ev", ascending=False)
    elif sort_mode == "🏆 Most Likely to Win":
        # Sort by the team with the highest win prob in the matchup
        df_sched_view["max_prob"] = df_sched_view[["home_win_prob", "away_win_prob"]].max(axis=1)
        df_sched_view = df_sched_view.sort_values(by="max_prob", ascending=False)
    else:
        df_sched_view = df_sched_view.sort_values(by="upset_score", ascending=False)

    st.info(f"Showing {total_count} games sorted by: {sort_mode}. Simulation Mode uses theoretical -110 lines where markets are closed.")
    
    for idx, row in df_sched_view.iterrows():
        # Display Mode Label
        badge_color = "#818cf8" if row["data_type"] == "💎 Market Alpha" else "#64748b"
        st.markdown(f"<span style='background: {badge_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; color: #fff; font-weight: 700;'>{row['data_type']}</span>", unsafe_allow_html=True)
        
        with st.expander(f"{row['away_team']} @ {row['home_team']} | {row['formatted_time']}"):
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                st.write(f"**{row['away_team']}**")
                st.write(f"Win Prob: {row['away_win_prob']*100:.1f}%")
                st.write(f"Proj Runs: {row['away_proj']:.1f}")
                st.write(f"Pitcher: {row['away_pitcher']}")
            with c2:
                st.write("**Matchup Info**")
                st.write(f"Elo Diff: {abs(int(row['home_elo']) - int(row['away_elo']))}")
                status_color = "#10b981" if row['status'] == "Live" else "#64748b"
                st.markdown(f"Status: <span style='color:{status_color}'>{row['status']}</span>", unsafe_allow_html=True)
                if row["data_type"] == "🧪 Simulation Mode":
                    st.write(f"Sim. EV: {row['ev']*100:+.1f}%")
            with c3:
                st.write(f"**{row['home_team']}**")
                st.write(f"Win Prob: {row['home_win_prob']*100:.1f}%")
                st.write(f"Proj Runs: {row['home_proj']:.1f}")
                st.write(f"Pitcher: {row['home_pitcher']}")
            
            # Show odds if available
            game_odds = df_master[df_master["game_id"] == row["game_id"]]
            game_odds = game_odds[game_odds["odds"].notnull()]
            if not game_odds.empty:
                st.markdown("---")
                st.markdown("**Available Markets**")
                st.dataframe(game_odds[["bookmaker", "outcome", "odds", "implied_prob", "ev"]], use_container_width=True)
            else:
                st.warning("No live market odds found. Displaying Elo-based Simulation data (-110 base).")

elif page == "📈 Team Power Rankings":
    st.subheader("🏆 Global Leaderboard: Elo Point Scores")
    elo_map = load_elo_ratings()
    elo_df = pd.DataFrame(list(elo_map.items()), columns=['Team', 'Elo']).sort_values(by='Elo', ascending=False)
    st.dataframe(elo_df.reset_index(drop=True), use_container_width=True)
    st.markdown("---")
    fig = px.bar(elo_df, x='Elo', y='Team', orientation='h', color='Elo', text='Elo', color_continuous_scale='Viridis', template='plotly_dark')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(height=1000, margin=dict(l=20, r=20, t=20, b=20), yaxis={'categoryorder':'total ascending'}, xaxis_title="Elo Points Score", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

elif page == "🧬 Player WAR Analytics":
    st.subheader("🧬 Player WAR Analytics")
    if os.path.exists("data/raw/player_war_2024.csv"):
        df_war = pd.read_csv("data/raw/player_war_2024.csv")
        fig_war = px.treemap(df_war, path=['Team', 'Name'], values='WAR', color='WAR', color_continuous_scale='RdYlGn', template='plotly_dark')
        fig_war.update_layout(margin=dict(t=30, b=10, r=10, l=10))
        st.plotly_chart(fig_war, use_container_width=True)
        st.dataframe(df_war.sort_values(by='WAR', ascending=False), use_container_width=True)
    else:
        st.info("Player WAR stats not found. Certification run required.")

st.markdown("---")
with st.expander("🔍 Market & Elo Depth (Raw Data)"):
    # Corrected df_odds to df_master
    st.dataframe(df_master, use_container_width=True)

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 50px; opacity: 0.6;'>
        <p>© 2026 BEST BETS Analytics Engine. Data by The Odds API, API-Sports & Balldontlie.</p>
        <p style='font-size: 0.8rem;'>Sports betting involves risk. Wager only what you can afford to lose.</p>
    </div>
""", unsafe_allow_html=True)

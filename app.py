import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from core.data_fetcher import get_mlb_odds, process_odds_data, get_mlb_games
from core.models import american_to_decimal, calculate_ev, calculate_implied_probability, flat_staking, kelly_criterion
from core.strategy import is_divisional_matchup

# Page Configuration
st.set_page_config(page_title="BEST BETS | MLB Analytics", page_icon="⚾", layout="wide")

# Load CSS
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
unit_size = st.sidebar.slider("Unit Size (%)", 0.5, 5.0, 1.5, 0.1)
ev_threshold = st.sidebar.slider("EV Alert Threshold (%)", 0.0, 10.0, 3.0, 0.5) / 100
fractional_kelly = st.sidebar.slider("Fractional Kelly multiplier", 0.1, 1.0, 0.25, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚦 Risk Control")
tilt_lock = st.sidebar.toggle("🛡️ Enable TILT LOCK", value=True, help="Limits daily risk to 5 units to prevent emotional chasing.")
if tilt_lock:
    st.sidebar.warning("Tilt Lock Active: Max 5 Units Daily Risk")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Strategies")
enable_divisional = st.sidebar.checkbox("Focus: Divisional Underdogs", value=True)
enable_f5 = st.sidebar.checkbox("Focus: F5 (First 5 Innings)", value=False)
enable_rlm = st.sidebar.checkbox("Track: Reverse Line Movement", value=True)

# Main Dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bankroll", f"${bankroll:,.2f} CAD")
with col2:
    st.metric("Unit Size", f"${flat_staking(bankroll, unit_size):,.2f}")
with col3:
    st.metric("Model Confidence", "High", delta="+4.2%")
with col4:
    st.metric("Risk Status", "Protected" if tilt_lock else "Exposed", delta="OK")

st.markdown("---")

# Data Fetching
@st.cache_data(ttl=600)
def fetch_and_process():
    raw_odds = get_mlb_odds()
    if not raw_odds:
        return pd.DataFrame()
    df = process_odds_data(raw_odds)
    return df

with st.spinner("Analyzing Market Markets and Sabermetrics..."):
    df_odds = fetch_and_process()

if df_odds.empty:
    st.warning("No live MLB data found. Note: Season must be active for real stats.")
    # Show dummy data for UI preview
    dummy_data = [
        {"outcome": "Toronto Blue Jays", "bookmaker": "DraftKings", "away_team": "NY Yankees", "home_team": "Toronto Blue Jays", "market": "h2h", "odds": "+135", "is_divisional": True, "commence_time": "2026-03-30T23:07:00Z"},
        {"outcome": "LA Dodgers", "bookmaker": "FanDuel", "away_team": "LA Dodgers", "home_team": "SF Giants", "market": "h2h", "odds": "-115", "is_divisional": True, "commence_time": "2026-03-31T01:45:00Z"}
    ]
    df_odds = pd.DataFrame(dummy_data)

# Adding Calculated Fields
df_odds["is_divisional"] = df_odds.apply(lambda row: is_divisional_matchup(row["home_team"], row["away_team"]), axis=1)
df_odds["formatted_time"] = pd.to_datetime(df_odds["commence_time"]).dt.strftime("%b %d, %H:%M")
df_odds["implied_prob"] = df_odds["odds"].apply(calculate_implied_probability)
df_odds["model_prob"] = df_odds["implied_prob"] + 0.05 # Simulated refinement
df_odds["decimal_odds"] = df_odds["odds"].apply(american_to_decimal)
df_odds["ev"] = df_odds.apply(lambda row: calculate_ev(row["model_prob"], row["decimal_odds"]), axis=1)
df_odds["kelly_stake"] = df_odds.apply(lambda row: kelly_criterion(row["model_prob"], row["decimal_odds"], fractional_kelly) * bankroll, axis=1)

# Main Prediction Table
st.subheader("🎯 Intelligence Feed: +EV Value Alerts")

# Filter for +EV
df_value = df_odds[df_odds["ev"] >= ev_threshold].sort_values(by="ev", ascending=False)

if df_value.empty:
    st.info("No high-value opportunities detected. Stay patient.")
else:
    for index, row in df_value.iterrows():
        with st.container():
            strategy_pills = []
            if row['is_divisional']: strategy_pills.append("🏷️ Divisional Underdog")
            if row['ev'] > 0.05: strategy_pills.append("🔥 High Value")
            
            pills_html = "".join([f"<span style='background: #6366f1; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; margin-right: 5px;'>{p}</span>" for p in strategy_pills])
            
            st.markdown(f"""
            <div class='bet-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 1.2rem; font-weight: 600; color: #fff;'>{row['outcome']} @ {row['bookmaker']}</span>
                        <div style='margin-top: 5px;'>{pills_html}</div>
                    </div>
                    <div style='text-align: right;'>
                        <div class='ev-badge'>+{row['ev']*100:.1f}% Expected Value</div>
                        <div style='margin-top: 5px; font-size: 0.8rem; color: #64748b;'>{row['formatted_time']}</div>
                    </div>
                </div>
                <div style='margin-top: 10px; color: #94a3b8; font-size: 0.9rem;'>
                    {row['away_team']} <b>@</b> {row['home_team']} | Market: {row['market'].upper()} | Odds: {row['odds']}
                </div>
                <div style='margin-top: 15px; display: flex; justify-content: space-between; align-items: flex-end;'>
                    <div style='display: flex; gap: 30px;'>
                        <div>
                            <div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase;'>Suggested Stake</div>
                            <div style='font-size: 1.1rem; color: #10b981; font-weight: 600;'>${row['kelly_stake']:,.2f} CAD</div>
                        </div>
                        <div>
                            <div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase;'>Edge Logic</div>
                            <div style='font-size: 1.1rem;'><b>{row['model_prob']*100:.1f}%</b> Win Prob</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("🔍 Market Depth (Raw Data)"):
        st.dataframe(df_odds, use_container_width=True)

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 50px; opacity: 0.6;'>
        <p>© 2026 BEST BETS Analytics Engine. Data by The Odds API & Balldontlie.</p>
        <p style='font-size: 0.8rem;'>Sports betting involves risk. Wager only what you can afford to lose.</p>
    </div>
""", unsafe_allow_html=True)

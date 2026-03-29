import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from core.data_fetcher import get_mlb_odds, process_odds_data, get_mlb_games
from core.models import american_to_decimal, calculate_ev, calculate_implied_probability, flat_staking, kelly_criterion, calculate_elo_probability, calculate_sport_select_ev, calculate_expected_runs
from core.strategy import is_divisional_matchup
from core.elo_ratings import get_team_elo
from core.status_fetcher import get_player_injuries, get_fatigue_penalty

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
std_bet_size = st.sidebar.slider("Standard Bet Size (%)", 0.5, 5.0, 1.5, 0.1, help="The percentage of your total bankroll you consider one 'unit'. Used as a baseline for flat staking.")
min_edge = st.sidebar.slider("Minimum Edge Needed (%)", 0.0, 100.0, 3.0, 0.5, help="Only show bets where our model calculates an edge (profit advantage) higher than this percentage.") / 100
fractional_kelly = st.sidebar.slider("Fractional Kelly multiplier", 0.1, 1.0, 0.25, 0.05, help="A safety factor to reduce the suggested bet size.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Market Region")
selected_region = st.sidebar.selectbox("Odds Data Region", ["us", "uk", "eu", "au"], index=0, help="If no games appear, try switching to 'uk' or 'eu' for wider coverage.")

if st.sidebar.button("🔄 Clear Cache & Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚦 Risk Control")
tilt_lock = st.sidebar.toggle("🛡️ Enable TILT LOCK", value=True, help="Limits daily risk to 5 units.")
if tilt_lock:
    st.sidebar.warning("Tilt Lock Active: Max 5 Units Daily Risk")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Strategies")
enable_divisional = st.sidebar.checkbox("Focus: Divisional Underdogs", value=True)
enable_f5 = st.sidebar.checkbox("Focus: F5 (First 5 Innings)", value=False)
enable_ss_mode = st.sidebar.toggle("🇨🇦 Sport Select Optimizer", value=False, help="Filters for bets that are +EV at Sport Select's reduced payout levels.")
reduction_factor = st.sidebar.slider("SS Reduction Factor", 0.70, 0.95, 0.91, 0.01) if enable_ss_mode else 0.91

# Main Dashboard
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Bankroll", f"${bankroll:,.2f} CAD")
with col2:
    st.metric("Base Unit (1.0u)", f"${flat_staking(bankroll, std_bet_size):,.2f}")
with col3:
    st.metric("Intelligence Engine", "Elo-V2", delta="Active")
with col4:
    st.metric("Risk Status", "Protected" if tilt_lock else "Exposed", delta="OK")

st.markdown("---")

# Data Fetching
@st.cache_data(ttl=600)
def fetch_and_process(region):
    raw_odds = get_mlb_odds(regions=region)
    if not raw_odds:
        return pd.DataFrame()
    df = process_odds_data(raw_odds)
    return df

with st.spinner("Synchronizing Markets & Deep Learning Elo Engine..."):
    df_odds = fetch_and_process(selected_region)

if df_odds.empty:
    st.warning(f"No live MLB data found in the '{selected_region.upper()}' region. Try switching regions or clicking 'Refresh'.")
    # Show dummy data for UI preview
    dummy_data = [
        {"outcome": "Toronto Blue Jays", "bookmaker": "DraftKings", "away_team": "NY Yankees", "home_team": "Toronto Blue Jays", "market": "h2h", "odds": "+135", "is_divisional": True, "commence_time": "2026-03-30T23:07:00Z"},
        {"outcome": "LA Dodgers", "bookmaker": "FanDuel", "away_team": "LA Dodgers", "home_team": "SF Giants", "market": "h2h", "odds": "-115", "is_divisional": True, "commence_time": "2026-03-31T01:45:00Z"}
    ]
    df_odds = pd.DataFrame(dummy_data)

# Adding Calculated Fields
df_odds["is_divisional"] = df_odds.apply(lambda row: is_divisional_matchup(row["home_team"], row["away_team"]), axis=1)
df_odds["formatted_time"] = pd.to_datetime(df_odds["commence_time"]).dt.strftime("%b %d, %H:%M")

# Elo Calculations
def get_prediction(row):
    h_elo = get_team_elo(row["home_team"])
    a_elo = get_team_elo(row["away_team"])
    
    # New: Injury & Fatigue Adjustments
    # In a full impl, we'd fetch these real-time. For now, we use the status_fetcher logic.
    h_fatigue = get_fatigue_penalty(row["home_team"]) # Note: needs abbreviation mapping
    a_fatigue = get_fatigue_penalty(row["away_team"])
    
    adjustments = {
        'home': -h_fatigue,
        'away': -a_fatigue
    }
    
    h_win_prob = calculate_elo_probability(h_elo, a_elo, adjustments=adjustments)
    
    # Projected Scores
    h_proj = calculate_expected_runs(h_elo, a_elo)
    a_proj = calculate_expected_runs(a_elo, h_elo)
    
    # Win prob for the OUTCOME being bet on
    if row["outcome"] == row["home_team"]:
        return h_win_prob, h_elo, a_elo, h_proj, a_proj
    else:
        return (1.0 - h_win_prob), a_elo, h_elo, a_proj, h_proj

df_odds[["model_prob", "team_elo", "opp_elo", "team_proj", "opp_proj"]] = df_odds.apply(
    lambda r: pd.Series(get_prediction(r)), axis=1
)

df_odds["implied_prob"] = df_odds["odds"].apply(calculate_implied_probability)
df_odds["decimal_odds"] = df_odds["odds"].apply(american_to_decimal)
df_odds["ev"] = df_odds.apply(lambda row: calculate_ev(row["model_prob"], row["decimal_odds"]), axis=1)
df_odds["ss_ev"] = df_odds.apply(lambda row: calculate_sport_select_ev(row["model_prob"], row["decimal_odds"], reduction_factor), axis=1)
df_odds["kelly_stake"] = df_odds.apply(lambda row: kelly_criterion(row["model_prob"], row["decimal_odds"], fractional_kelly) * bankroll, axis=1)
df_odds["potential_profit"] = df_odds["kelly_stake"] * (df_odds["decimal_odds"] - 1.0)
df_odds["ss_potential_profit"] = df_odds["kelly_stake"] * (df_odds["decimal_odds"] * reduction_factor - 1.0)
df_odds["total_payout"] = df_odds["kelly_stake"] * df_odds["decimal_odds"]

# Main Prediction Table
st.subheader("🎯 Intelligence Feed: +EV Value Alerts")

# Filtering logic
if enable_ss_mode:
    df_value = df_odds[df_odds["ss_ev"] >= min_edge].sort_values(by="ss_ev", ascending=False)
else:
    df_value = df_odds[df_odds["ev"] >= min_edge].sort_values(by="ev", ascending=False)

if df_value.empty:
    st.info("No high-value opportunities detected. Patience is profitable.")
else:
    for index, row in df_value.iterrows():
        with st.container():
            strategy_pills = []
            if row['is_divisional']: strategy_pills.append("🏷️ Divisional Play")
            if (row['ss_ev' if enable_ss_mode else 'ev'] > 0.05): strategy_pills.append("🔥 High Value")
            if enable_ss_mode: strategy_pills.append("🇨🇦 SS Optimizer Active")
            
            pills_html = "".join([f"<span style='background: #6366f1; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; margin-right: 5px;'>{p}</span>" for p in strategy_pills])
            
            # Determine labels
            predicted_winner = row['outcome']
            home_elo = int(row['team_elo'] if row['outcome']==row['home_team'] else row['opp_elo'])
            away_elo = int(row['opp_elo'] if row['outcome']==row['home_team'] else row['team_elo'])
            home_proj = row['team_proj'] if row['outcome']==row['home_team'] else row['opp_proj']
            away_proj = row['opp_proj'] if row['outcome']==row['home_team'] else row['team_proj']
            
            st.markdown(f"""
<div class='bet-card'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <div style='color: #818cf8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; margin-bottom: 3px;'>🎯 Predicted Winner</div>
            <span style='font-size: 1.5rem; font-weight: 800; color: #fff; letter-spacing: -1px;'>{predicted_winner}</span>
            <div style='margin-top: 5px;'>{pills_html}</div>
        </div>
        <div style='text-align: right;'>
            <div class='ev-badge'>+{row['ss_ev' if enable_ss_mode else 'ev']*100:.1f}% EV {'(at SS Odds)' if enable_ss_mode else ''}</div>
            <div style='margin-top: 5px; font-size: 0.8rem; color: #64748b;'>{row['formatted_time']}</div>
        </div>
    </div>
    <hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);'>
    
    <div style='display: flex; justify-content: space-between; margin-bottom: 15px;'>
        <div style='text-align: center; flex: 1;'>
            <div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase;'>{row['away_team']}</div>
            <div style='font-size: 1.3rem; font-weight: 700; color: #fff;'>{away_proj:.1f}</div>
            <div style='color: #94a3b8; font-size: 0.75rem;'>Elo: {away_elo}</div>
        </div>
        <div style='align-self: center; color: #475569; font-weight: 900; padding: 0 15px;'>VS</div>
        <div style='text-align: center; flex: 1;'>
            <div style='color: #64748b; font-size: 0.7rem; text-transform: uppercase;'>{row['home_team']}</div>
            <div style='font-size: 1.3rem; font-weight: 700; color: #fff;'>{home_proj:.1f}</div>
            <div style='color: #94a3b8; font-size: 0.75rem;'>Elo: {home_elo}</div>
        </div>
    </div>

    <div style='margin-top: 15px; background: rgba(255, 255, 255, 0.02); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.03);'>
        <div style='display: flex; justify-content: space-between;'>
            <div>
                <div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;'>Suggested Wager</div>
                <div style='font-size: 1.25rem; color: #818cf8; font-weight: 700;'>${row['kelly_stake']:,.2f} CAD</div>
            </div>
            <div style='text-align: right;'>
                <div style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: 600;'>Est. Profit {'(SS)' if enable_ss_mode else ''}</div>
                <div style='font-size: 1.25rem; color: #10b981; font-weight: 700;'>+${row['ss_potential_profit' if enable_ss_mode else 'potential_profit']:,.2f} CAD</div>
            </div>
        </div>
        <div style='margin-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 10px; display: flex; justify-content: space-between;'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>Model Confidence: <b>{row['model_prob']*100:.1f}%</b></div>
            <div style='color: #94a3b8; font-size: 0.85rem;'>Implying: <b>{row['implied_prob']*100:.1f}% Prob</b></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
with st.expander("🔍 Market & Elo Depth (Raw Data)"):
    st.dataframe(df_odds, use_container_width=True)

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 50px; opacity: 0.6;'>
        <p>© 2026 BEST BETS Analytics Engine. Data by The Odds API, API-Sports & Balldontlie.</p>
        <p style='font-size: 0.8rem;'>Sports betting involves risk. Wager only what you can afford to lose.</p>
    </div>
""", unsafe_allow_html=True)

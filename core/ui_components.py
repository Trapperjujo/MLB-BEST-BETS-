import streamlit as st
import pandas as pd

def render_strategy_rationale(row, best_bet):
    """
    🔬 Institutional Strategy Rationale
    Translates statistical alpha into plain-English betting strategy.
    """
    if best_bet['ev'] <= 0:
        return
    
    alpha_pct = (row['home_win_prob'] - best_bet.get('implied_prob', 0.5)) * 100
    h_team = row['home_team']
    
    st.markdown(f"""
    <div style='background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 10px; border-radius: 4px; margin-top: 10px;'>
        <div style='font-size: 0.8rem; color: #10b981; font-weight: 800; text-transform: uppercase;'>🔬 Institutional Alpha Rationale</div>
        <div style='font-size: 0.85rem; color: #fff; margin-top: 5px; line-height: 1.4;'>
            The 70/30 Hybrid Model identifies a <b>{alpha_pct:.1f}% raw edge</b> on <b>{h_team if row['home_win_prob'] > 0.5 else row['away_team']}</b>. 
            The market is currently underpricing the <b>Process Anchor</b> (Advanced Pitching metrics) compared to the public standings results.
        </div>
        <div style='font-size: 0.75rem; color: #94a3b8; font-style: italic; margin-top: 5px;'>
            Strategy: Institutional Kelly stake is recommended to capture this market divergence.
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_matchup_card(row, best_bet, display_date, off_pct, live_score_html=""):
    """
    🏛️ Institutional Matchup Card (Phase 24 Rendering)
    Standardizes risk badging, 70/30 win probabilities, and EV alerts.
    """
    h_prob = row['home_win_prob']
    off_pct_val = float(off_pct)
    
    # 💎 Institutional Risk Profiling
    abs_diff = abs(h_prob - off_pct_val)
    if abs_diff < 0.05:
        risk_badge = "<span class='risk-badge-low' title='💎 Model results and official standings align (low outlier risk).'>💎 LOW VOLATILITY</span>"
    elif abs_diff < 0.15:
        risk_badge = "<span class='risk-badge-med' title='⚖️ Slight seasonal variance. Reliable institutional signal.'>⚖️ BALANCED CALIBRATION</span>"
    else:
        risk_badge = f"<span class='risk-badge-high' title='⚠️ High divergence between stats-model and standings results. High volatility scenario.'>⚠️ DIVERGENCE: {abs_diff*100:.1f}%</span>"

    # ⚡ Synergy Badge
    synergy_badge = f"<span class='synergy-badge' title='⚡ High-Fidelity Signal: Both our Stats-Model and the XGBoost Alpha model agree on the outcome.'>⚡ XGBoost Consensus</span>" if (row['home_win_prob'] > 0.5 and row['xg_prob'] > 0.5) or (row['home_win_prob'] < 0.5 and row['xg_prob'] < 0.5) else ""
    
    # 🧬 Market Wager HTML
    wager_html = f"""<div title="🎲 Institutional Staking: Based on your bankroll and the calculated edge." style='font-size: 0.8rem; color: var(--neon-green); font-weight: 700; margin-top: 5px;'>Wager: ${best_bet['kelly_stake']:,.2f} CAD</div>
<div title="💰 Potential Profit: Calculated at current market odds." style='font-size: 0.7rem; color: #fff;'>Est. Profit: +${best_bet['potential_profit']:,.2f}</div>""" if best_bet['kelly_stake'] > 0 else f"""<div title="Institutional Logic: The market price accurately reflects the true probability. No profitable edge identified." style='font-size: 0.7rem; color: #94a3b8; font-weight: 700; margin-top: 8px; border: 1px solid rgba(255,255,255,0.1); padding: 4px; border-radius: 4px; cursor: help;'>🧬 MARKET EFFICIENCY: PASS</div>
<div style='font-size: 0.6rem; color: #64748b; margin-top: 2px;'>No institutional edge identified</div>"""

    data_source = best_bet.get("data_source", "🛰️ Scraper Fallback")
    
    # Render Main Card
    card_html = f"""<div class='neon-card'>
<div class='neon-card-header'>
<div style='display: flex; align-items: center; gap: 10px;'>
<span style='font-size: 1.1rem;'>📅 {display_date}</span>
<span class='alpha-badge' title='🛰️ Data Stream: Identifies which institutional feed confirmed this signal.'>{data_source}</span>
{risk_badge}
{synergy_badge}
</div>
{f"<div class='ev-badge' title='🎯 Expected Value: The mathematical edge identified over the current market price.'>+{best_bet['ev']*100:.1f}% EV</div>" if best_bet['ev'] > 0 else "<div class='ev-badge' style='background: rgba(148,163,184,0.1); color: #94a3b8;' title='Market is efficient. No profitable edge present.'>EFFICIENT</div>"}
</div>
<div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center; align-items: center;'>
<div>
<div style='color: var(--text-secondary); font-size: 0.75rem;'>AWAY</div>
<div style='font-size: 1.1rem; font-weight: 800; color: #fff;'>{row['away_team']}</div>
<div style='color: var(--neon-green); font-size: 1.4rem; font-weight: 900;' title='Pro-Ball Win Probability for the Away team.'>{row['away_win_prob']*100:.1f}%</div>
<div style='font-size: 0.8rem; color: #94a3b8; font-weight: 500;' title='Institutional Strength Metric: Calculated from historical outcomes.'>Hybrid Elo: {int(row['away_elo'])}</div>
</div>
<div style='display: flex; flex-direction: column; justify-content: center; align-items: center; border-left: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); padding: 0 10px;'>
<div style='font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px;' title='The 70/30 Hybrid Model predicts this team as the likely winner.'>Winner (70/30)</div>
<div style='font-size: 1.2rem; font-weight: 900; color: #fff; line-height: 1.1; margin: 4px 0;'>{row['home_team'] if row['home_win_prob'] > 0.5 else row['away_team']}</div>
<div style='font-size: 0.7rem; color: var(--neon-blue); font-weight: 700;' title='The institutional confidence level of the current signal.'>Confidence: {row['xg_conf']*100:.1f}%</div>
{wager_html}
{live_score_html}
</div>
<div>
<div style='color: var(--text-secondary); font-size: 0.75rem;'>HOME</div>
<div style='font-size: 1.1rem; font-weight: 800; color: #fff;'>{row['home_team']}</div>
<div style='font-size: 0.7rem; color: #94a3b8; margin-bottom: 5px;' title='Ground-truth standing anchor for home-field calculation.'>Official Standings: .{int(off_pct_val*1000)}</div>
<div style='color: var(--neon-green); font-size: 1.4rem; font-weight: 900;' title='Pro-Ball Win Probability for the Home team.'>{row['home_win_prob']*100:.1f}%</div>
<div style='font-size: 0.8rem; color: #94a3b8; font-weight: 500;' title='Institutional Strength Metric: Calculated from historical outcomes.'>Hybrid Elo: {int(row['home_elo'])}</div>
</div>
</div>
<div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05); text-align: center;'>
<div style='font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 4px;'>INSTITUTIONAL PITCHER SNAPSHOT</div>
<div style='font-size: 0.9rem; font-weight: 700; color: #fff;' title='Probable Pitchers and current seasonal ERA comparison.'>
{row.get('away_pitcher', 'TBD')} <span style='color: var(--neon-blue);'>({row['a_p_era']:.2f})</span> vs {row.get('home_pitcher', 'TBD')} <span style='color: var(--neon-green);'>({row['h_p_era']:.2f})</span>
</div>
</div>
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Render Strategy Rationale for +EV Signals
    render_strategy_rationale(row, best_bet)

def render_calibration_hud(row, off_pct, ground_truth=0.5):
    """
    ⚖️ Institutional Calibration HUD
    Compares Process (Advanced) vs Results (Standings) vs Reality (3-Season Ground Truth).
    """
    st.markdown("#### ⚖️ Institutional Calibration")
    c_model, c_anchor = st.columns(2)
    
    raw_elo = row.get('h_raw_elo', row['home_elo'])
    hybrid_elo = row['home_elo']
    elo_shift = hybrid_elo - raw_elo
    shift_icon = "📈" if elo_shift >= 0 else "📉"
    
    with c_model:
        st.write(f"**Process (70%):** {int(raw_elo)} Elo", help="Pure analytical strength without standings anchor.")
        st.write(f"**Results (30%):** {int((float(off_pct) - 0.5) * 1000 + 1500)} Elo", help="Strength based solely on current win/loss standings.")
        st.write(f"**Reality (Long):** {ground_truth*100:.1f}% Win Rate", help="3-Season historical performance (2024-2026).")
    
    with c_anchor:
        st.write(f"**Hybrid Elo:** {int(hybrid_elo)}", help="The final weighted strength used by the Monte Carlo engine.")
        st.write(f"**Anchor Shift:** {shift_icon} {abs(elo_shift):.1f} pts", help="The points difference added/removed by the 30% standings anchor.")
        
        # 🏛️ Calibration Health
        cal_diff = abs(row['home_win_prob'] - ground_truth)
        if cal_diff < 0.03:
            st.success("🎯 **GOLD CALIBRATION**", help="Excellent alignment with long-term historical trends.")
        elif cal_diff < 0.10:
            st.warning("⚖️ **STABLE SIGNAL**", help="Normal seasonal variance. Proceed with baseline risk.")
        else:
            st.error("⚠️ **HIGH DIVERGENCE**", help="Model is predicting a major outlier compared to history.")

def render_market_depth_hud(best_bet):
    """
    📊 Market Depth HUD
    Displays consensus pricing vs institutional alpha with Sharp benchmarking.
    """
    st.markdown("#### 📊 Market Depth & Liquidity")
    
    with st.expander("❔ **What is a 'Sharp' Benchmark?**"):
        st.markdown("""
        <div style='font-size: 0.85rem; color: #94a3b8; line-height: 1.4;'>
        <b>Institutional Logic:</b> In professional sports betting, <b>'Sharp'</b> refers to offshore bookmakers (like Pinnacle or Bookmaker.eu) that take high-limit wagers from professional bettors. 
        <br><br>
        Because 'Sharps' respect the professional money, their prices are often more accurate than the 'Square' (public) market. We track these prices to see if the professional money agrees with our model's signal.
        </div>
        """, unsafe_allow_html=True)

    m_info, m_consensus = st.columns(2)
    
    sources = best_bet.get('sources_count', 1)
    consensus_price = best_bet.get('market_avg', best_bet['odds'])
    sharp_price = best_bet.get('sharp_benchmark')
    
    with m_info:
        st.write(f"**Data Feeds:** {sources} Authorized", help="Cumulative number of sportsbooks currently active in the market.")
        st.write(f"**Public Average:** {int(consensus_price):+d}", help="Consensus price across recreational bookmakers.")
        if sharp_price:
            st.markdown(f"**Sharp Price:** <span style='color: #00f3ff; font-weight: 800;'>{int(sharp_price):+d}</span>", unsafe_allow_html=True)
        else:
            st.write("**Sharp Price:** 🛰️ Tracking...", help="Searching for institutional Price action (Pinnacle/Bookmaker).")
        
    with m_consensus:
        # Liquidity logic based on Sharp/Public divergence
        is_stale = False
        if sharp_price:
            is_stale = abs(best_bet['odds'] - float(sharp_price)) > 10
            
        alpha_status = "STALE" if is_stale else "LIQUID"
        status_color = "#00f3ff" if alpha_status == "LIQUID" else "#ff9900"
        st.markdown(f"**Market Status:** <span style='color: {status_color}; font-weight: 800;'>{alpha_status}</span>", unsafe_allow_html=True)
        
        if is_stale:
            st.warning("⚠️ Market Divergence", help="Current local book odds are drifting away from sharp consensus. High volatility.")
        else:
            st.success("💎 Consolidated", help="Market is tight and consensus is high. Efficient pricing.")

def render_profit_hud(row, best_bet, elo_shift):
    """
    💎 Profit Maximization HUD
    Displays Alpha Gap and Kelly Staking alerts.
    """
    st.markdown("#### 💎 Profit Maximization")
    p_model, p_market = st.columns(2)
    
    with p_model:
        st.metric("Model Win%", f"{row['home_win_prob']*100:.1f}%", f"{elo_shift:+.1f} Shift", help="The final win probability including and HFA and Hybrid anchors.")
    with p_market:
        market_implied = best_bet.get('implied_prob', 0)
        alpha_gap = (row['home_win_prob'] - market_implied) * 100
        st.metric("Alpha Gap", f"{alpha_gap:+.1f}%", "Relative to Market", help="The 'Edge' or 'Alpha' over the public market. Higher + gap = higher profit potential.")

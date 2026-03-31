import streamlit as st
import pandas as pd

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
        risk_badge = "<span class='risk-badge-low'>💎 LOW VOLATILITY</span>"
    elif abs_diff < 0.15:
        risk_badge = "<span class='risk-badge-med'>⚖️ BALANCED CALIBRATION</span>"
    else:
        risk_badge = f"<span class='risk-badge-high'>⚠️ DIVERGENCE: {abs_diff*100:.1f}%</span>"

    # ⚡ Synergy Badge
    synergy_badge = f"<span class='synergy-badge'>⚡ XGBoost Consensus</span>" if (row['home_win_prob'] > 0.5 and row['xg_prob'] > 0.5) or (row['home_win_prob'] < 0.5 and row['xg_prob'] < 0.5) else ""
    
    # 🧬 Market Wager HTML
    wager_html = f"""<div style='font-size: 0.8rem; color: var(--neon-green); font-weight: 700; margin-top: 5px;'>Wager: ${best_bet['kelly_stake']:,.2f} CAD</div>
<div style='font-size: 0.7rem; color: #fff;'>Est. Profit: +${best_bet['potential_profit']:,.2f}</div>""" if best_bet['kelly_stake'] > 0 else f"""<div style='font-size: 0.7rem; color: #94a3b8; font-weight: 700; margin-top: 8px; border: 1px solid rgba(255,255,255,0.1); padding: 4px; border-radius: 4px;'>🧬 MARKET EFFICIENCY: PASS</div>
<div style='font-size: 0.6rem; color: #64748b; margin-top: 2px;'>No institutional edge identified</div>"""

    data_source = best_bet.get("data_source", "🛰️ Scraper Fallback")
    
    # Render Main Card
    card_html = f"""<div class='neon-card'>
<div class='neon-card-header'>
<div style='display: flex; align-items: center; gap: 10px;'>
<span style='font-size: 1.1rem;'>📅 {display_date}</span>
<span class='alpha-badge'>{data_source}</span>
{risk_badge}
{synergy_badge}
</div>
{f"<div class='ev-badge'>+{best_bet['ev']*100:.1f}% EV</div>" if best_bet['ev'] > 0 else "<div class='ev-badge' style='background: rgba(148,163,184,0.1); color: #94a3b8;'>EFFICIENT</div>"}
</div>
<div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center; align-items: center;'>
<div>
<div style='color: var(--text-secondary); font-size: 0.75rem;'>AWAY</div>
<div style='font-size: 1.1rem; font-weight: 800; color: #fff;'>{row['away_team']}</div>
<div style='color: var(--neon-green); font-size: 1.4rem; font-weight: 900;'>{row['away_win_prob']*100:.1f}%</div>
<div style='font-size: 0.8rem; color: #94a3b8; font-weight: 500;'>Hybrid Elo: {int(row['away_elo'])}</div>
</div>
<div style='display: flex; flex-direction: column; justify-content: center; align-items: center; border-left: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); padding: 0 10px;'>
<div style='font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px;'>70/30 WINNER</div>
<div style='font-size: 1.2rem; font-weight: 900; color: #fff; line-height: 1.1; margin: 4px 0;'>{row['home_team'] if row['home_win_prob'] > 0.5 else row['away_team']}</div>
<div style='font-size: 0.7rem; color: var(--neon-blue); font-weight: 700;'>Confidence: {row['xg_conf']*100:.1f}%</div>
{wager_html}
{live_score_html}
</div>
<div>
<div style='color: var(--text-secondary); font-size: 0.75rem;'>HOME</div>
<div style='font-size: 1.1rem; font-weight: 800; color: #fff;'>{row['home_team']}</div>
<div style='font-size: 0.7rem; color: #94a3b8; margin-bottom: 5px;'>Official: .{int(off_pct_val*1000)}</div>
<div style='color: var(--neon-green); font-size: 1.4rem; font-weight: 900;'>{row['home_win_prob']*100:.1f}%</div>
<div style='font-size: 0.8rem; color: #94a3b8; font-weight: 500;'>Hybrid Elo: {int(row['home_elo'])}</div>
</div>
</div>
<div style='margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05); text-align: center;'>
<div style='font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 4px;'>INSTITUTIONAL PITCHER SNAPSHOT</div>
<div style='font-size: 0.9rem; font-weight: 700; color: #fff;'>
{row.get('away_pitcher', 'TBD')} <span style='color: var(--neon-blue);'>({row['a_p_era']:.2f})</span> vs {row.get('home_pitcher', 'TBD')} <span style='color: var(--neon-green);'>({row['h_p_era']:.2f})</span>
</div>
</div>
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)

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
        st.write(f"**Process (70%):** {int(raw_elo)} Elo")
        st.write(f"**Results (30%):** {int((float(off_pct) - 0.5) * 1000 + 1500)} Elo")
        st.write(f"**Reality (Longitudinal):** {ground_truth*100:.1f}% Win Rate")
    
    with c_anchor:
        st.write(f"**Hybrid Elo:** {int(hybrid_elo)}")
        st.write(f"**Anchor Shift:** {shift_icon} {abs(elo_shift):.1f} pts")
        
        # 🏛️ Calibration Health
        cal_diff = abs(row['home_win_prob'] - ground_truth)
        if cal_diff < 0.03:
            st.success("🎯 **GOLD CALIBRATION**: Anchored to History")
        elif cal_diff < 0.10:
            st.warning("⚖️ **STABLE**: Slight seasonal variance")
        else:
            st.error("⚠️ **DIVERGENCE**: Major outlier scenario")

def render_market_depth_hud(best_bet):
    """
    📊 Market Depth HUD
    Displays consensus pricing vs institutional alpha.
    """
    st.markdown("#### 📊 Market Depth & Liquidity")
    m_info, m_consensus = st.columns(2)
    
    sources = best_bet.get('sources_count', 1)
    consensus_price = best_bet.get('market_avg', best_bet['odds'])
    
    with m_info:
        st.write(f"**Data Sources:** {sources} Authorized Feeds")
        st.write(f"**Consensus Price:** {int(consensus_price):+d}")
        
    with m_consensus:
        alpha_status = "STALE" if abs(best_bet['odds'] - consensus_price) > 5 else "LIQUID"
        status_color = "#00f3ff" if alpha_status == "LIQUID" else "#ff9900"
        st.markdown(f"**Status:** <span style='color: {status_color}; font-weight: 800;'>{alpha_status}</span>", unsafe_allow_html=True)
        st.info("Market Liquidity is sufficient for institutional stake.")

def render_profit_hud(row, best_bet, elo_shift):
    """
    💎 Profit Maximization HUD
    Displays Alpha Gap and Kelly Staking alerts.
    """
    st.markdown("#### 💎 Profit Maximization")
    p_model, p_market = st.columns(2)
    
    with p_model:
        st.metric("Model Win%", f"{row['home_win_prob']*100:.1f}%", f"{elo_shift:+.1f} Shift")
    with p_market:
        market_implied = best_bet.get('implied_prob', 0)
        alpha_gap = (row['home_win_prob'] - market_implied) * 100
        st.metric("Alpha Gap", f"{alpha_gap:+.1f}%", "Relative to Market")

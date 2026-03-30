# 🛰️ SOP: MLB Situational Analysis & Profitability (2026 Season)

This Standard Operating Procedure (SOP) governs the probabilistic and analytical decision-making for the PRO BALL PREDICTOR 2026. You MUST follow these protocols to ensure 100% logic fidelity.

## 🎯 Phase 1: Institutional Calibration (10k Simulations)
- **Monte Carlo Engine:** 10,000 simulations per matchup using Poisson run-projection models.
- **HFA Buffer:** Always apply +24 Elo Home Field Advantage to the home team's run-line baseline.
- **Momentum Scaling:** Starting from Game 10, scale wRC+ momentum weighting from 10% to 30%.

## 💎 Phase 2: Situational Research (Statcast Matrix)
Analyze the **Statcast Matchup Matrix** for the following institutional alpha points:
- **xwOBA Drift:** Compare real-time contact quality against season averages.
- **Venue Alpha:** Ingest the **Park Factor** coefficient from `core/config.py`. Adjust projected run totals by the specified Run/HR bias.
- **Weather Factor:** Wind Blowing In @ 5+ MPH? Unders hit 55.1%. Wind Blowing Out? Lean Over.
- **Umpire Scoping:** Confirm umpire strike zone bias (Tight zones = more walks/Overs).

## 📊 Phase 3: Profitability & Staking (Non-Negotiables)
Calculate wagers using the **Fractional Kelly (0.25)** or **Flat Staking** models:
- **The Unit System:** 1 Unit = 1-2% of Total Bankroll.
- **Max Stake Cap:** Never allocate more than 3% to a single outcome regardless of confidence.
- **Stop-Loss Rule:** Pause/Review every 10 Units lost in a 7-day cycle.
- **CLV Tracking:** Monitor Closing Line Value consistently to identify SKILL vs. LUCK.

## 📡 Phase 4: Market Intelligence (High-Value Angles)
- **Divisional Underdogs:** Prioritize +Money payouts in rivalry games (+51.34 Units historical alpha).
- **First 5 Innings (F5):** Utilize when starting pitching advantage is high but bullpen variance is a risk.
- **Reverse Line Movement (RLM):** Monitor for line movement opposite to public betting. Divisional underdogs with RLM are a Tier-1 "Sharp Money" signal.

## 🍱 Phase 5: Master Feed Rendering
Ensure every card reflects:
1. **Model Confidence (%)** vs. **Market Implied (%)**
2. **Kelly Suggested Stake (CAD)** vs. **Flat Unit Stake (CAD)**
3. **Live Score Alignment (tank01 Sync)**
4. **Venue Alpha Status** (e.g., "+5.5% Run Bias")

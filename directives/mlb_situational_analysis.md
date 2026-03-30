# 🛰️ SOP: MLB Situational Analysis (2026 Season)

This Standard Operating Procedure (SOP) governs the probabilistic and analytical decision-making for the PRO BALL PREDICTOR 2026. You MUST follow these protocols to ensure 100% logic fidelity.

## 🎯 Phase 1: Institutional Calibration
- **Monte Carlo Engine:** 10,000 simulations per matchup. Do NOT deviate to lower iteration counts for "speed"—precision is the priority.
- **HFA Buffer:** Always apply the +24 Elo Home Field Advantage buffer to the home team's run-line baseline.
- **Momentum Alpha:** Starting from Game 10 of the 2026 season, scale the wRC+ momentum weight from 10% to 30%.

## 💎 Phase 2: Situational Research (Statcast Matrix)
Analyze the **Statcast Matchup Matrix** for the following institutional alpha points:
- **xwOBA Drift:** If a hitter's xwOBA is > .360 against the specific pitcher's primary archetypes (e.g., High-Fastball, Sweeper), adjust win confidence by +2.5%.
- **Venue Alpha:** Ingest the **Park Factor** coefficient from `core/config.py`. Adjust projected run totals by the specified Run/HR bias.
- **Bat Tracking:** If a starter's "Blasts" percentage (Swing Speed + Squared-Up) is significantly above the 2025 mean, prioritize the 'Ceiling (75%)' score cluster.

## 📈 Phase 3: Stake Optimization (Kelly Criterion)
Calculate wagers using the **Fractional Kelly (0.25)** criterion:
- **Bankroll Security:** Never allocate more than 3% of the total bankroll to a single outcome (Max Stake Cap).
- **EV Threshold:** Only flag wagers with an Expected Value (+EV) of >3.5%.

## 🍱 Phase 4: Master Feed Rendering
Ensure that every card in the dashboard reflects:
1. **Model Confidence (%)**
2. **Implied Probability (%)**
3. **Kelly Suggested Stake (CAD)**
4. **Live Score Alignment (tank01 Sync)**

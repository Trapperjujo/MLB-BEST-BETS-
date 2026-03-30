# 🎯 Analytical Strategy: Project North Star

> **Directive Version**: 2026.03.30.01  
> **Status**: Institutional Baseline  
> **Core Principle**: "The goal isn't to predict every winner—it's to find mispriced odds where our probability assessment differs meaningfully from the market's."

---

## 🔍 Layer 1: Data Foundations (The Intelligence Feed)

We prioritize high-fidelity, institutional data over volume.

### 1. Official Performance Metrics (Statcast)
- **Pitching**: Focus on **ERA, FIP, WAR, and K/9**. These represent the true skill vs outcome delta.
- **Hitting**: Focus on **OPS and wRC+** (Institutionally adjusted for park factors/100 average).
- **Injury/Fatigue**: Ingest real-time lineup changes and secondary data (e.g., bullpens status).
- **Strategic Foundations**: Consult [MLB Betting Foundations](file:///c:/Users/clear/MLB/directives/mlb_betting_foundations.md) for 2026 Season betting trends, advanced metrics (RPI/Pythagorean), and situational research.

### 2. Market Alpha Data
- **Live Odds**: Continuous polling of **The Odds API** (30+ global books).
- **Implied Probabilities**: P(book) = 1 / decimal_odds. Always consider the "Vig" as the house hurdle.
- **CLV (Closing Line Value)**: Our success metric is consistently beating the final market price.

---

## 🧠 Layer 2: Analytical Framework (The Engine)

### 🏟️ CORE METHODOLOGY
Our predictive engine utilizes **Elo Ratings**, **XGBoost v3.0**, and **Monte Carlo Simulations**.

- **Elo Foundations**: See [elo_foundations.md](file:///c:/Users/clear/MLB/directives/elo_foundations.md) for theory and implementation.
- **Sabermetrics Foundations**: See [sabermetrics_foundations.md](file:///c:/Users/clear/MLB/directives/sabermetrics_foundations.md) for historical context.

### 1. Predictive Synergy
We use a 2-Layer simulation architecture:
- **Layer A (Monte Carlo)**: 10,000 iterations using Poisson-distributed run scoring.
- **Layer B (XGBoost v3)**: Longitudinal ML filtering for non-linear situational edges (e.g., Pitcher vs Hitting profiles).

### 2. Edge Identification
**Bet Only When**: $P(model) > P(book) + \text{Margin Threshold}$
- *Example*: Model @ 45% vs Market @ 35% = 10% Alpha Gap.

---

## 💰 Layer 3: Profitability & Risk Control (The Bankroll)

### 1. The Staking Hierarchy
- **Primary Strategy**: **Quarter-Kelly (0.25)**. 
- **Methodology**: Stake = $0.25 \times \frac{(B \times P) - Q}{B}$
  - *Where B = Decimal Odds - 1, P = Win Prob, Q = Loss Prob.*
- **Outcome**: Achieves ~75% of Full Kelly's growth with only ~25% of the volatility.

### 2. Operational Guards
- **Max Unit Size**: 1.5% of total bankroll (Baseline).
- **Absolute Cap**: **3.0% Maximum stake per wager**, regardless of model confidence.
- **Stop-Loss**: Automated pause if 10 units are lost in a single standard week.

---

## 🚀 Execution Checklist
- [ ] **Verify Alpha**: No bet placed without positive expected value (+EV).
- [ ] **Data Quality**: Prioritize verified institutional feeds over public narrative.
- [ ] **Emotion Control**: Flat staking or Quarter-Kelly ONLY. No "chasing" losses.
- [ ] **Auditing**: Track ROI, Win Rate, and CLV metrics daily.

---
*© 2026 BEST BETS Predictive Terminal. Strategic Ground Truth.*

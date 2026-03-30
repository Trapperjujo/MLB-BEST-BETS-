# ⚾ WAR Intelligence & Player Ratings

> **Directive Version**: 2026.03.30.01  
> **Source Ground Truth**: FanGraphs (fWAR) / Baseball-Reference (bWAR)  
> **Definition**: "Wins Above Replacement" (WAR) estimates the total win contribution a player provides over a theoretical "replacement-level" player (~.294 winning percentage).

---

## 📊 1. WAR Rating Scale (Betting Context)

| WAR Range | Player Tier | Strategic Betting Relevance |
| :--- | :--- | :--- |
| **8.0+** | 🏆 **MVP Candidate** | High-impact futures; extreme market movement on injury. |
| **5.0 – 8.0** | ⭐ **All-Star** | Strong lineup/prop value; foundational "Alpha" contributor. |
| **2.0 – 5.0** | ⚾ **Above-Average** | Solid role player; provides stability to betting spreads. |
| **0.0 – 2.0** | 🧊 **Bench/Replacement** | Minimal betting impact; easily replaceable in simulation. |
| **< 0.0** | ⚠️ **Below Replacement** | Potential regression candidate; "Negative Value" risk. |

---

## 🧠 2. Analytical Application

### 🛰️ Institutional Baseline
- **fWAR (FanGraphs)**: Preferred for **situational modeling** (includes FIP and fielding metrics).
- **bWAR (Bref)**: Preferred for **historical backtesting** (results-oriented).

### 📈 Betting Workflow
1. **MVP Futures**: Cross-reference market odds with current WAR leaderboards. Top-10 WAR only.
2. **Team Win Totals**: Summing cumulative projected WAR for a 2026 roster correlates directly with win-total efficiency.
3. **Injury Devaluation**:
   - $\text{Win Loss} = (\text{WAR of Injured Player}) - (\text{WAR of Replacement})$
   - *Example*: 5-WAR SS injured $\rightarrow$ 0-WAR Replacement $\rightarrow$ Expect ~5 fewer wins over a full season.

### 💎 Finding the Edge
- **Under-Valued**: A low ERA pitcher with high FIP but **low WAR** might be "luck-dependent."
- **Over-Valued**: A player with high traditional stats (HR/RBI) but **low WAR** is likely being over-hyped by public sentiment.

---

## 🛠️ Execution Logic (Terminal Sync)
- [x] **Pitcher Matrix**: Bubble size in the matrix reflects **WAR** (Standard 2025-2026 calibration).
- [x] **Lineup Shifts**: Any roster change calculates the "WAR Delta" to adjust simulation win-probs (Implemented in `get_prediction`).
- [x] **Regression Monitoring**: Audit players with "Negative WAR" for systematic -EV betting alerts (Implemented in dashboard Regression tab).

---
*© 2026 BEST BETS Predictive Terminal. Institutional Player Analytics.*

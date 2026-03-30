# TeamRankings MLB Integration Directive (Layer 1)

This directive defines the Standard Operating Procedure (SOPs) for integrating [TeamRankings](https://www.teamrankings.com/mlb/) high-fidelity betting trends and predictive analytics into the **MLB Predictive Terminal** workflow.

## 📡 Objectives
1.  **Situational Analysis**: Monitor Run Line and Over/Under trends to identify market mispricings.
2.  **Predictive Calibration**: Use TeamRankings PPR (Predictive Power Ranking) as a validation layer for XGBoost v3.0 projections.
3.  **Data Synergy**: Cross-reference market alpha from TeamRankings with current project Elo ratings.

## 🛰️ Step-by-Step Execution

### 1. Daily Ingestion (Level 3 Scripts)
- **Tool**: `execution/bulk_scraper.py`
- **Action**: Fetch current **Win %**, **Run Line %**, and **O/U %** for all 30 teams.
- **Reference**: [TeamRankings URL reference](file:///C:/Users/clear/.gemini/antigravity/knowledge/MLB_DATA_ATLAS/artifacts/team_rankings_reference.md).

### 2. Form Alignment check
- **Condition**: If a team's Run Line (ATS) success rate is > 5% higher than their moneyline win rate, flag them as "Public Value Underdogs" (PVU).
  - *Example*: Detroit Tigers (2025-2026) outperforming Run Line expectations specifically in interleague play.

### 3. Strength of Schedule (SoS) Normalization
- **SOP**: Adjust model confidence levels based on TeamRankings SoS. 
  - Teams with SoS in the Top 5 and current Win % > 55% receive a **High-Fidelity Alpha Boost (+0.05)**.

### 4. Over/Under "Park Factor Tax"
- **Action**: Adjust total run projections based on TeamRankings historical "Over" trends for specific park/window combinations (Day vs Night).

## 🧬 Validation Logic
- **Primary Check**: Compare XGBoost ML win probability vs. TeamRankings implied probability (from Moneyline).
- **Secondary Check**: Ensure that all team abbreviations (e.g., `NYM` vs `METS`) are aligned using the project [Abbreviation Mapping](file:///c:/Users/clear/MLB/test_abbrs.py).

## 🚀 Post-Action Reporting
- Every 1,000 simulations, the model must output a **"TeamRankings Variance Report"** highlighting discrepancies between historical trends (Atlas) and current-form metrics.

> [!IMPORTANT]
> This directive is a living document. Any structural shifts in TeamRankings URL schemes must be immediately updated in the [Reference Artifact](file:///C:/Users/clear/.gemini/antigravity/knowledge/MLB_DATA_ATLAS/artifacts/team_rankings_reference.md).

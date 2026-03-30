# Institutional API Reference: PRO BALL PREDICTOR (2026)

This document specifies the technical contracts and logic schemas for the 2026 terminal architecture. It is designed to ensure long-term maintenance and multi-agent interoperability.

## 🧬 Data Contracts (Pydantic V2)
The terminal enforces strict type-safety through three core schemas located in `core/schemas.py`.

### 1. `MLBPlayer`
Defines the state of a player (Hitter or Pitcher) during a high-sigma simulation.
- **Fields**: `id: int`, `name: str`, `team: str`, `era: float`, `fip: float`, `war: float`.

### 2. `MLBGame`
Defines the metadata and logistical parameters of a scheduled matchup.
- **Fields**: `game_id: str`, `home_team: str`, `away_team: str`, `commence_time: datetime`, `home_pitcher: str`, `away_pitcher: str`.

### 3. `MLBPrediction`
The ultimate output of the predictive engine.
- **Fields**: `game_id: str`, `home_win_prob: float`, `away_win_prob: float`, `ev: float` (Edge percentage).

---

## 🏛️ Historical SQL Layer (DuckDB)
Historical analytics are performed via the in-memory DuckDB layer in `core/database.py`.

### Table: `game_outcomes`
Stores the longitudinal dataset of 7,748+ games.
- **Key Columns**: `game_id`, `home_team`, `away_team`, `home_score`, `away_score`, `was_home_fav`.

### Table: `situational_alpha`
Stores mapped situational trends (e.g., Park Factors, Umpire Bias).
- **Key Columns**: `year`, `team`, `variable`, `alpha_coefficient`.

---

## 🛡️ Error Taxonomy (Loguru Standard)
To ensure millisecond response-time during 2026 Opening Weekend, the terminal uses structured error codes.

| Code | Severity | Meaning | Resolution |
| :--- | :--- | :--- | :--- |
| `ERR_API_TIMEOUT` | CRITICAL | MLB Stats API or Odds API failed to respond. | Verify `.env` keys and network. |
| `ERR_DATA_DRIFT` | WARNING | Input data (ERA/Elo) outside normal distribution. | Check `verify_upgrade.py` logs. |
| `ERR_SIM_SIGMA` | INFO | Monte Carlo simulation hit a high-variance outlier. | Logic feed annotated with ⚠️. |

---

## 🛰️ Integration Patterns
### Analytical Tracking
The `AlphaTracker` service in `core/analytics.py` logs decisions to `analytics/decision_log.json`.
- **Naming Pattern**: `object_action_context`
- **Example**: `signal_depth_viewed` for expanding a matchup card.

import os

# Season Metadata
CURRENT_SEASON = 2026
HISTORICAL_SEASONS = [2024, 2025, 2026]

# Risk Management
KELLY_MODES = {
    'Full': 1.0,
    'Half': 0.5,
    'Quarter': 0.25
}
DEFAULT_KELLY_MODE = 'Quarter'
MAX_STAKE_CAP = 0.03 # 3% Maximum bankroll allocation per bet

# Model Constants
MLB_HFA = 24 # Standard Home Field Advantage Elo Adjustment
ELO_K_FACTOR = 4.0 # Sensitivity of predictions
FRACTIONAL_KELLY = 0.25 # Risk reduction factor for Kelly Criterion (fallback)

# View Settings
MIN_EDGE_DEFAULT = 3.0 # % Edge needed for Intelligence Feed flags
BANKROLL_DEFAULT = 5000.0 # CAD Baseline
STD_BET_SIZE_DEFAULT = 1.5 # % of bankroll per unit
CAD_USD_XRATE = 1.35 # Default CAD conversion factor

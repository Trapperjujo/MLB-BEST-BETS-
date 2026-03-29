import os

# Season Metadata
CURRENT_SEASON = 2026

# Model Constants
MLB_HFA = 24 # Standard Home Field Advantage Elo Adjustment
ELO_K_FACTOR = 4.0 # Sensitivity of predictions
FRACTIONAL_KELLY = 0.25 # Risk reduction factor for Kelly Criterion

# View Settings
MIN_EDGE_DEFAULT = 3.0 # % Edge needed for Intelligence Feed flags
BANKROLL_DEFAULT = 5000.0 # CAD Baseline
STD_BET_SIZE_DEFAULT = 1.5 # % of bankroll per unit

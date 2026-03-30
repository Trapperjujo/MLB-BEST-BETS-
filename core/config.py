import os
from dotenv import load_dotenv

# Season Metadata
DEPLOYMENT_VERSION = "2026.03.30.02" # Incremental version to force cache invalidation
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

# Institutional Park Factors (2024-2026 Roll-Forward Baseline)
# Base: 100.0 (Standard Run Environment)
MLB_PARK_FACTORS = {
    "Colorado Rockies": {"run": 115.0, "hr": 112.0, "desc": "High altitude; extreme offensive inflation."},
    "San Diego Padres": {"run": 94.0, "hr": 92.0, "desc": "Marine layer; heavy pitcher bias."},
    "Seattle Mariners": {"run": 91.0, "hr": 94.0, "desc": "Dead-ball environment; lowest run-scoring potential."},
    "Cincinnati Reds": {"run": 105.0, "hr": 125.0, "desc": "Launchpad; major power-hitting inflation."},
    "New York Yankees": {"run": 98.0, "hr": 118.0, "desc": "Short porch; extreme HR sensitivity."},
    "Baltimore Orioles": {"run": 96.0, "hr": 92.0, "desc": "Left-field wall deep; defensive inflation."},
    "Toronto Blue Jays": {"run": 99.0, "hr": 102.0, "desc": "Neutral environment; symmetrical dimensions."},
    "Los Angeles Dodgers": {"run": 99.0, "hr": 115.0, "desc": "Warm air; seasonal power-hitting bias."},
    "Arizona Diamondbacks": {"run": 101.0, "hr": 98.0, "desc": "Humidified air; stable scoring environment."},
    "San Francisco Giants": {"run": 94.0, "hr": 89.0, "desc": "Cold air; extreme long-ball suppression."},
    "Default": {"run": 100.0, "hr": 100.0, "desc": "Standard league-average environment."}
}

# --- STATS API BRIDGE ---

# Model Constants
MC_ITERATIONS = 10000 # Institutional baseline for Monte Carlo simulations
MLB_HFA = 24 # Standard Home Field Advantage Elo Adjustment
ELO_K_FACTOR = 4.0 # Sensitivity of predictions
FRACTIONAL_KELLY = 0.25 # Risk reduction factor for Kelly Criterion (fallback)

# View Settings
MIN_EDGE_DEFAULT = 3.0 # % Edge needed for Intelligence Feed flags
BANKROLL_DEFAULT = 5000.0 # CAD Baseline
STD_BET_SIZE_DEFAULT = 1.5 # % of bankroll per unit
CAD_USD_XRATE = 1.35 # Default CAD conversion factor

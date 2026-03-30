import os
from dotenv import load_dotenv

# Season Metadata
DEPLOYMENT_VERSION = "2026.03.30.04" # Institutional March 30 intelligence layer
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
    "Colorado Rockies": {"run": 115.0, "hr": 112.0, "k_factor": 85.0, "desc": "High altitude; extreme offensive inflation."},
    "San Diego Padres": {"run": 94.0, "hr": 92.0, "k_factor": 105.0, "desc": "Marine layer; heavy pitcher bias."},
    "Seattle Mariners": {"run": 81.0, "hr": 71.0, "k_factor": 122.0, "desc": "Dead-ball environment; lowest run-scoring potential."},
    "Cincinnati Reds": {"run": 105.0, "hr": 125.0, "k_factor": 108.0, "desc": "Launchpad; major power-hitting inflation."},
    "New York Yankees": {"run": 98.0, "hr": 118.0, "k_factor": 104.0, "desc": "Short porch; extreme HR sensitivity."},
    "Baltimore Orioles": {"run": 96.0, "hr": 92.0, "k_factor": 102.0, "desc": "Left-field wall deep; defensive inflation."},
    "St. Louis Cardinals": {"run": 98.0, "hr": 95.0, "k_factor": 100.0, "desc": "Neutral-to-pitcher leaning; Busch Stadium stability."},
    "Toronto Blue Jays": {"run": 99.0, "hr": 102.0, "k_factor": 100.0, "desc": "Neutral environment; symmetrical dimensions."},
    "Los Angeles Dodgers": {"run": 99.0, "hr": 115.0, "k_factor": 106.0, "desc": "Warm air; seasonal power-hitting bias."},
    "Arizona Diamondbacks": {"run": 101.0, "hr": 98.0, "k_factor": 98.0, "desc": "Humidified air; stable scoring environment."},
    "San Francisco Giants": {"run": 94.0, "hr": 89.0, "k_factor": 110.0, "desc": "Cold air; extreme long-ball suppression."},
    "Oakland Athletics": {"run": 108.0, "hr": 105.0, "k_factor": 102.0, "desc": "Sutter Health Park (Sacramento); high-offense volatility; low-altitude thermal."},
    "Default": {"run": 100.0, "hr": 100.0, "k_factor": 100.0, "desc": "Standard league-average environment."}
}

# April Weather Situational Alphas (2026)
WEATHER_ALPHAS = {
    "cold_temp_threshold": 50.0, # °F
    "velocity_tax": -1.5, # mph loss on fastballs below threshold
    "batted_ball_drag": -3.3, # feet lost per 10°F drop
    "wind_under_signal": 8.0, # mph blowing IN triggers high-confidence Under
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

# 🛰️ 2026 League Environment (Guts)
# These constants define the mathematical baseline for XGBoost and Monte Carlo normalization.
LEAGUE_GUTS_2026 = {
    "wOBA": 0.310,
    "wOBA_scale": 1.325,
    "r_pa": 0.112,      # Runs per Plate Appearance
    "cfip": 2.911,      # League Average FIP Constant
    "base_runs_pg": 4.56 # Derived 2026 average runs per game
}

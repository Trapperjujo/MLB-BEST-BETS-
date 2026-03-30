import os
from dotenv import load_dotenv

# Load Environment Variables from Root .env
# This is the single Institutional Source of Truth for the 2026 Season (Phase 16).
load_dotenv()

# --- SEASON & DEPLOYMENT ---
VERSION = "2026.03.30.05"
DEPLOYMENT_VERSION = VERSION # Institutional Alias for UI Coordination
SEASON = 2026
HISTORICAL_SEASONS = [2024, 2025, 2026]
TERMINAL_NAME = "PRO BALL PREDICTOR"
TERMINAL_TAGLINE = "Institutional Research Terminal for Canadian Sabermetrics Analysis."

# --- PERSISTENCE LAYER ---
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "terminal_2026.duckdb")
HISTORICAL_DIR = os.path.join(DB_DIR, "historical")
CACHE_DIR = ".cache"

# --- RISK MANAGEMENT (KELLY / BANKROLL) ---
KELLY_MODES = {
    'Full': 1.0,
    'Half': 0.5,
    'Quarter': 0.25
}
DEFAULT_KELLY_MODE = 'Quarter'
FRACTIONAL_KELLY = 0.25
MAX_STAKE_CAP = 0.03 # 3% Maximum bankroll allocation per bet
STD_BET_SIZE_DEFAULT = 1.5
MIN_EDGE_DEFAULT = 3.0 # %
BANKROLL_DEFAULT = 5000.0
CAD_USD_XRATE = 1.35

# --- ASSET PATHS (HARDCODING SHIELD) ---
ASSETS = {
    "CSS": ["styles/main.css", "styles/neon_theme.css"],
    "LOGS": "logs/terminal_2026.log"
}

# --- COMPLIANCE & SEO (HARDCODING SHIELD) ---
SEO = {
    "TITLE": "PRO BALL PREDICTOR | MLB Analytics Terminal 2026",
    "DESC": "Institutional-grade MLB predictive analytics terminal using XGBoost v3.0 and Monte Carlo simulations for 2026 season projections. Verified 61.6% accuracy audit.",
    "KEYWORDS": "MLB Predictions, 2026 World Series Odds, MLB Expert Picks, Statcast Data, Baseball Analytics, XGBoost MLB, MLB Betting Alpha, MLB Futures Bets, MLB Player Props, Shohei Ohtani Odds"
}

LEGAL_SHIELD = """
<div class="responsible-gaming-alert">
    🎯 <b>RESPONSIBLE GAMING NOTICE:</b> Must be 19+ to participate. If you or someone you know has a gambling problem, call 1-866-531-2600 (ConnexOntario). 
    Predictions are for educational/informational purposes only. <b>NOT FINANCIAL ADVICE.</b>
</div>
"""

# --- ALGORITHMIC CONSTANTS ---
MC_ITERATIONS = 10000
MLB_HFA = 24
ELO_K_FACTOR = 4.0

# --- LEAGUE ENVIRONMENT (2026 GUTS) ---
LEAGUE_GUTS = {
    "wOBA": 0.310,
    "wOBA_scale": 1.325,
    "r_pa": 0.112,
    "cfip": 2.911,
    "base_runs_pg": 4.56
}

# --- PARK FACTOR BASELINE ---
PARK_FACTORS = {
    "Colorado Rockies": {"run": 115.0, "hr": 112.0, "k_factor": 85.0},
    "San Diego Padres": {"run": 94.0, "hr": 92.0, "k_factor": 105.0},
    "Seattle Mariners": {"run": 81.0, "hr": 71.0, "k_factor": 122.0},
    "Cincinnati Reds": {"run": 105.0, "hr": 125.0, "k_factor": 108.0},
    "New York Yankees": {"run": 98.0, "hr": 118.0, "k_factor": 104.0},
    "Baltimore Orioles": {"run": 96.0, "hr": 92.0, "k_factor": 102.0},
    "St. Louis Cardinals": {"run": 98.0, "hr": 95.0, "k_factor": 100.0},
    "Toronto Blue Jays": {"run": 99.0, "hr": 102.0, "k_factor": 100.0},
    "Los Angeles Dodgers": {"run": 99.0, "hr": 115.0, "k_factor": 106.0},
    "Arizona Diamondbacks": {"run": 101.0, "hr": 98.0, "k_factor": 98.0},
    "San Francisco Giants": {"run": 94.0, "hr": 89.0, "k_factor": 110.0},
    "Oakland Athletics": {"run": 108.0, "hr": 105.0, "k_factor": 102.0},
    "Default": {"run": 100.0, "hr": 100.0, "k_factor": 100.0}
}

# --- SECURITY & KEYS ---
def get_rapid_key():
    return os.getenv("API_SPORTS_KEY") or os.getenv("RAPIDAPI_KEY")

def get_balldontlie_key():
    return os.getenv("BALLDONTLIE_API_KEY")

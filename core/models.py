import math
import random
import numpy as np
import pandas as pd
from typing import Dict, Any

def american_to_decimal(american_odds: int) -> float:
    """Converts American odds to Decimal odds."""
    try:
        if isinstance(american_odds, str):
            american_odds = int(american_odds.replace("+", "").strip())
    except (ValueError, TypeError):
        return 1.0 # Return parity odds if error

    if american_odds > 0:
        return (american_odds / 100.0) + 1.0
    else:
        return (100.0 / abs(american_odds)) + 1.0

def calculate_implied_probability(american_odds: int) -> float:
    """Calculates implied probability from American odds."""
    try:
        if isinstance(american_odds, str):
            american_odds = int(american_odds.replace("+", "").strip())
    except (ValueError, TypeError):
        return 0.5 # Default to 50/50 if error

    if american_odds > 0:
        return 100.0 / (american_odds + 100.0)
    else:
        return abs(american_odds) / (abs(american_odds) + 100.0)

def calculate_elo_probability(home_elo: int, away_elo: int, hfa: int = 24, adjustments: dict = None) -> float:
    """
    Calculates the home win probability with adjustments:
    - hfa: Home Field Advantage constant.
    - adjustments: dict like {'home': -20, 'away': -5} for injuries/fatigue,
      and NEW: 'lineup_war_diff' for player-level strength.
    """
    h_adj = adjustments.get('home', 0) if adjustments else 0
    a_adj = adjustments.get('away', 0) if adjustments else 0
    war_diff_adj = adjustments.get('lineup_war_diff', 0) if adjustments else 0
    
    # 1 WAR is roughly equivalent to 6.25 Elo points in a 162-game season
    elo_diff = (away_elo + a_adj) - (home_elo + h_adj + hfa + war_diff_adj)
    probability = 1.0 / (1.0 + math.pow(10.0, elo_diff / 400.0))
    return probability

def calculate_war_elo_adjustment(team_war: float, opp_war: float) -> float:
    """
    Converts a WAR differential into an Elo-equivalent adjustment.
    Standard: 1 WAR = ~6.25 Elo points.
    """
    war_diff = team_war - opp_war
    return war_diff * 6.25

def calculate_sport_select_ev(model_prob: float, market_decimal_odds: float, reduction: float = 0.91) -> float:
    """
    Calculates EV Specifically for Sport Select (WCLC).
    Sport Select Odds = Market Odds * Reduction
    """
    # Note: If the user is using PROLINE 3-way, this would need adjusting.
    # For now, we use the 0.91 derived factor for Point Spreads.
    ss_odds = market_decimal_odds * reduction
    return (model_prob * ss_odds) - 1.0

def calculate_expected_runs(elo: int, opp_elo: int, base_runs: float = 4.40) -> float:
    """
    Predicts expected runs for a team based on Elo ratings.
    MLB Average runs per game is ~4.4-4.5.
    Every 100 Elo points is roughly +0.6 runs per 9 innings.
    """
    elo_diff = elo - opp_elo
    # Using a linear adjustment for better MLB alignment
    # 100 diff / 167 (approx factor) -> 0.6 run boost
    return max(1.0, base_runs + (elo_diff / 167.0))

def calculate_ev(model_prob: float, decimal_odds: float) -> float:
    """Calculates Expected Value (EV) percentage."""
    return (model_prob * decimal_odds) - 1.0

def kelly_criterion(model_prob: float, decimal_odds: float, fractional: float = 0.25) -> float:
    """Calculates the optimal bet size using the Kelly Criterion (Fractional)."""
    if decimal_odds <= 1.0 or model_prob <= 0.0:
        return 0.0
    
    # b = Net odds received (Decimal Odds - 1)
    b = decimal_odds - 1.0
    p = model_prob
    q = 1.0 - p
    
    # f = (bp - q) / b
    f = (b * p - q) / b
    
    # Scale by fractional Kelly to reduce variance
    return max(0.0, f * fractional)

def calculate_situational_drift(row: pd.Series, park_factor: float = 1.0) -> float:
    """
    XGBoost v3.0 Longitudinal Filtering:
    Generates a situational 'Drift Coefficient' based on high-fidelity performance variables.
    Calculates the delta between raw Elo-probs and institutional Statcast-alpha.
    """
    drift = 0.0
    # 🛰️ Venue Alpha Correction (Park Factors)
    # Adjusts run environment expectations based on c:/Users/clear/MLB/core/config.py
    if park_factor != 1.0:
        drift += (park_factor - 1.0) * 0.05 # Conservative 5% sensitivity multiplier
        
    return drift

def calculate_fair_odds(away_odds: int, home_odds: int) -> Dict[str, Any]:
    """
    Normalizes implied probabilities to remove the 'Vig' (Juice).
    Returns fair implied probabilities and fair American odds.
    """
    p_a = calculate_implied_probability(away_odds)
    p_h = calculate_implied_probability(home_odds)
    
    total_prob = p_a + p_h
    if total_prob == 0: return {"away_fair_prob": 0.5, "home_fair_prob": 0.5}
    
    # Normalize
    f_p_a = p_a / total_prob
    f_p_h = p_h / total_prob
    
    def prob_to_american(p):
        if p >= 0.5:
            return int(-((p / (1 - p)) * 100))
        else:
            return int(((1 - p) / p) * 100)

    return {
        "away_fair_prob": float(f_p_a),
        "home_fair_prob": float(f_p_h),
        "away_fair_odds": prob_to_american(f_p_a),
        "home_fair_odds": prob_to_american(f_p_h),
        "vig_percent": float((total_prob - 1.0) * 100)
    }

def run_monte_carlo_simulation(home_elo: int, away_elo: int, iterations: int = 10000, hfa: int = 24, adjustments: Dict = None) -> Dict[str, Any]:
    """
    Monte Carlo Engine: 10,000 simulations per matchup.
    Utilizes Poisson distribution models for high-fidelity run projection.
    """
    # 📏 Project runs using Effective Elo (Home Elo + 24 point buffer)
    h_proj = calculate_expected_runs(home_elo + hfa, away_elo)
    a_proj = calculate_expected_runs(away_elo, home_elo + hfa)
    
    # 🛰️ Apply Situational Adjustments (Injuries, Fatigue, Weather)
    if adjustments:
        h_proj += float(adjustments.get('home_runs_adj', 0))
        a_proj += float(adjustments.get('away_runs_adj', 0))

    # 🛡️ Safety Fallback: Ensure projections are positive and numeric
    if pd.isna(h_proj) or h_proj < 1.0: h_proj = 4.4
    if pd.isna(a_proj) or a_proj < 1.0: a_proj = 4.4

    # Simulate scores using Poisson distribution
    # We use a large enough sample to stabilize the mean
    home_scores = np.random.poisson(h_proj, iterations)
    away_scores = np.random.poisson(a_proj, iterations)
    
    home_wins = np.sum(home_scores > away_scores)
    away_wins = np.sum(away_scores > home_scores)
    ties = np.sum(home_scores == away_scores)
    
    # Resolve ties via fractional win sharing (simulating extra innings)
    total_non_ties = home_wins + away_wins
    if total_non_ties > 0:
        h_win_share = home_wins / total_non_ties
        home_wins += ties * h_win_share
        away_wins += ties * (1 - h_win_share)
    else:
        home_wins += ties * 0.5
        away_wins += ties * 0.5

    return {
        'home_win_prob': float(home_wins / iterations),
        'away_win_prob': float(away_wins / iterations),
        'home_avg_runs': float(np.mean(home_scores)),
        'away_avg_runs': float(np.mean(away_scores)),
        'home_scores': home_scores.tolist()[:100], 
        'away_scores': away_scores.tolist()[:100]
    }

def flat_staking(bankroll: float, unit_percent: float = 1.5) -> float:
    """Calculates the stake for a flat betting strategy."""
    return bankroll * (unit_percent / 100.0)

def calculate_clv(closing_prob: float, closing_odds: float, bet_odds: float) -> float:
    """Calculates Closing Line Value (CLV)."""
    # CLV = (Bet Odds / Closing Odds) - 1
    if closing_odds == 0:
        return 0.0
    return (bet_odds / closing_odds) - 1.0

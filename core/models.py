import math
import random
import numpy as np

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

def run_monte_carlo_simulation(home_elo: int, away_elo: int, iterations: int = 10000, adjustments: dict = None) -> dict:
    """
    Runs a Monte Carlo simulation for an MLB game.
    Returns: {
        'home_win_prob': float,
        'away_win_prob': float,
        'home_avg_runs': float,
        'away_avg_runs': float,
        'over_total_prob': dict # (e.g. {7.5: 0.55})
    }
    """
    h_proj = calculate_expected_runs(home_elo, away_elo)
    a_proj = calculate_expected_runs(away_elo, home_elo)
    
    # Apply adjustments to the base projections if provided
    if adjustments:
        h_proj += adjustments.get('home_runs_adj', 0)
        a_proj += adjustments.get('away_runs_adj', 0)

    # Simulate scores using Poisson distribution (standard for baseball runs)
    home_scores = np.random.poisson(h_proj, iterations)
    away_scores = np.random.poisson(a_proj, iterations)
    
    # Calculate wins (handling ties as push/half-win depending on model, 
    # but in MLB games don't end in ties, so we simulate until a winner)
    # For simulation purposes, if tied, we give 0.5 to each or re-simulate.
    # Here we use the direct comparison:
    home_wins = np.sum(home_scores > away_scores)
    away_wins = np.sum(away_scores > home_scores)
    ties = np.sum(home_scores == away_scores)
    
    # Resolve ties by distributing based on win probability (simulating extra innings)
    total_non_ties = home_wins + away_wins
    if total_non_ties > 0:
        h_win_share = home_wins / total_non_ties
        home_wins += ties * h_win_share
        away_wins += ties * (1 - h_win_share)
    else:
        # Extreme edge case: project 50/50
        home_wins += ties * 0.5
        away_wins += ties * 0.5

    return {
        'home_win_prob': float(home_wins / iterations),
        'away_win_prob': float(away_wins / iterations),
        'home_avg_runs': float(np.mean(home_scores)),
        'away_avg_runs': float(np.mean(away_scores)),
        'home_scores': home_scores.tolist()[:100], # Sample for visualization
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

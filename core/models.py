import math

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
    - adjustments: dict like {'home': -20, 'away': -5} for injuries/fatigue.
    """
    h_adj = adjustments.get('home', 0) if adjustments else 0
    a_adj = adjustments.get('away', 0) if adjustments else 0
    
    elo_diff = (away_elo + a_adj) - (home_elo + h_adj + hfa)
    probability = 1.0 / (1.0 + math.pow(10.0, elo_diff / 400.0))
    return probability

def calculate_sport_select_ev(model_prob: float, market_decimal_odds: float, reduction: float = 0.91) -> float:
    """
    Calculates EV Specifically for Sport Select (WCLC).
    Sport Select Odds = Market Odds * Reduction
    """
    # Note: If the user is using PROLINE 3-way, this would need adjusting.
    # For now, we use the 0.91 derived factor for Point Spreads.
    ss_odds = market_decimal_odds * reduction
    return (model_prob * ss_odds) - 1.0

def calculate_expected_runs(elo: int, opp_elo: int, base_runs: float = 4.48) -> float:
    """
    Predicts expected runs for a team based on Elo ratings.
    Uses the 1500 baseline (average) as base_runs.
    """
    elo_diff = elo - opp_elo
    # Every 100 Elo points ~ 10-15% run variation
    run_multiplier = 10**(elo_diff / 800.0)
    return base_runs * run_multiplier

def calculate_ev(model_prob: float, decimal_odds: float) -> float:
    """Calculates Expected Value (EV) percentage."""
    return (model_prob * decimal_odds) - 1.0

def kelly_criterion(model_prob: float, decimal_odds: float, fractional: float = 0.25) -> float:
    """Calculates the optimal bet size using the Kelly Criterion (Fractional)."""
    if decimal_odds <= 1.0:
        return 0.0
    
    # b = Net odds received (Decimal Odds - 1)
    b = decimal_odds - 1.0
    p = model_prob
    q = 1.0 - p
    
    # f = (bp - q) / b
    if b == 0:
        return 0.0
        
    f = (b * p - q) / b
    
    # Scale by fractional Kelly to reduce variance
    return max(0.0, f * fractional)

def flat_staking(bankroll: float, unit_percent: float = 1.5) -> float:
    """Calculates the stake for a flat betting strategy."""
    return bankroll * (unit_percent / 100.0)

def calculate_clv(closing_prob: float, closing_odds: float, bet_odds: float) -> float:
    """Calculates Closing Line Value (CLV)."""
    # CLV = (Bet Odds / Closing Odds) - 1
    if closing_odds == 0:
        return 0.0
    return (bet_odds / closing_odds) - 1.0

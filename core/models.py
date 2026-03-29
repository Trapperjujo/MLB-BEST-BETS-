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

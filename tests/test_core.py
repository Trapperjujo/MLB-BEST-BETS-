import pytest
import pandas as pd
from core.models import (
    american_to_decimal, 
    calculate_implied_probability, 
    calculate_elo_probability, 
    calculate_ev, 
    kelly_criterion,
    calculate_expected_runs
)
from core.elo_ratings import normalize_team_name, get_team_elo

def test_odds_conversion():
    assert american_to_decimal(100) == 2.0
    assert american_to_decimal(-110) == pytest.approx(1.909, 0.001)
    assert american_to_decimal("+150") == 2.5
    assert american_to_decimal("-200") == 1.5

def test_implied_probability():
    assert calculate_implied_probability(100) == 0.5
    assert calculate_implied_probability(-110) == pytest.approx(0.5238, 0.0001)

def test_elo_probability():
    # 1500 vs 1500 should be 0.5 (ignoring HFA for base test)
    prob = calculate_elo_probability(1500, 1500, hfa=0)
    assert prob == 0.5
    
    # Home team stronger
    prob = calculate_elo_probability(1600, 1500, hfa=0)
    assert prob > 0.5
    
    # Test with HFA
    prob = calculate_elo_probability(1500, 1500, hfa=24)
    assert prob > 0.5 # Home should have advantage

def test_kelly_criterion():
    # 55% win prob, 2.0 odds (EV = 10%)
    # Full Kelly: (2.0*0.55 - 0.45)/1.0 = 0.11 or 11%
    # Quarter Kelly (0.25): 0.11 * 0.25 = 0.0275 or 2.75%
    stake = kelly_criterion(0.55, 2.0, fractional=0.25)
    assert stake == 0.0275
    
    # Negative EV should return 0
    stake = kelly_criterion(0.40, 2.0)
    assert stake == 0.0

def test_expected_runs():
    # Base 1500 vs 1500 -> ~4.4
    runs = calculate_expected_runs(1500, 1500)
    assert runs == 4.4
    
    # 1600 vs 1500 (+100 diff) -> +0.6 runs
    runs = calculate_expected_runs(1600, 1500)
    assert runs == pytest.approx(5.0, 0.1)

def test_normalization():
    assert normalize_team_name("D-backs") == "Arizona Diamondbacks"
    assert normalize_team_name("Blue Jays") == "Toronto Blue Jays"
    assert normalize_team_name("NY Yankees") == "NY Yankees" # Standard check

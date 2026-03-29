import sys
import os
import pandas as pd

# Mock Streamlit for testing core logic
class MockSt:
    def cache_data(self, func=None, **kwargs):
        if func is None:
            return lambda f: f
        return func

import streamlit as st
st.cache_data = MockSt().cache_data

from core.elo_ratings import load_elo_ratings, get_team_elo
from core.models import calculate_elo_probability, calculate_war_elo_adjustment

def test_elo_baselines():
    print("--- Testing ELO Baselines ---")
    elo_map = load_elo_ratings()
    print(f"Total teams in map: {len(elo_map)}")
    assert len(elo_map) >= 30, f"Expected 30+ teams, got {len(elo_map)}"
    
    # Check a few specific teams
    test_teams = ["Toronto Blue Jays", "Los Angeles Dodgers", "Chicago White Sox"]
    for team in test_teams:
        elo = get_team_elo(team)
        print(f"{team}: {elo}")
        assert elo > 1000 and elo < 2000, f"Suspicious ELO for {team}: {elo}"

def test_war_logic():
    print("\n--- Testing WAR Integration ---")
    h_war = 45.0 # High talent team
    a_war = 30.0 # Standard team
    adj = calculate_war_elo_adjustment(h_war, a_war)
    print(f"WAR Diff (15.0) -> Elo Adj: {adj}")
    assert adj == 15.0 * 6.25, f"Incorrect WAR adjustment: {adj}"

def test_probability_math():
    print("\n--- Testing Probability Math ---")
    # Home 1600, Away 1400, HFA 24
    h_elo = 1600
    a_elo = 1400
    prob = calculate_elo_probability(h_elo, a_elo, hfa=24)
    print(f"1600 vs 1400 (HFA 24) -> Home Win Prob: {prob*100:.1f}%")
    assert prob > 0.7, f"Probability too low for +200 Elo gap: {prob}"

if __name__ == "__main__":
    try:
        test_elo_baselines()
        test_war_logic()
        test_probability_math()
        print("\n[PASS] Verification Successful!")
    except Exception as e:
        print(f"\n[FAIL] Verification Failed: {e}")
        sys.exit(1)

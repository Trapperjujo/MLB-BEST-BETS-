import sys
import os

# Add project root to sys path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.models import run_monte_carlo_simulation, kelly_criterion

def test_mc_simulation():
    print("Testing Monte Carlo Simulation...")
    home_elo = 1600
    away_elo = 1550
    mc = run_monte_carlo_simulation(home_elo, away_elo, iterations=1000)
    print(f"  Home Win Prob: {mc['home_win_prob']:.2f}")
    print(f"  Away Win Prob: {mc['away_win_prob']:.2f}")
    print(f"  Home Avg Runs: {mc['home_avg_runs']:.1f}")
    print(f"  Away Avg Runs: {mc['away_avg_runs']:.1f}")
    assert mc['home_win_prob'] > 0.5
    print("  MC Simulation passed.")

def test_kelly_logic():
    print("Testing Kelly Criterion Logic...")
    prob = 0.55
    odds = 2.0 # American +100
    
    # Full Kelly: (2.0 * 0.55 - 0.45) / 1.0 = 0.1 / 1.0 = 0.1
    k_full = kelly_criterion(prob, odds, fractional=1.0)
    print(f"  Full Kelly: {k_full:.2f}")
    assert round(k_full, 2) == 0.10
    
    # Quarter Kelly: 0.1 * 0.25 = 0.025
    k_q = kelly_criterion(prob, odds, fractional=0.25)
    print(f"  Quarter Kelly: {k_q:.2f}")
    assert round(k_q, 3) == 0.025
    print("  Kelly logic passed.")

if __name__ == "__main__":
    try:
        test_mc_simulation()
        test_kelly_logic()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)

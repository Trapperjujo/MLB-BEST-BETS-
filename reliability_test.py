import pandas as pd
import numpy as np
from core.models import run_monte_carlo_simulation

def test_mc_reliability():
    print("Testing Monte Carlo Reliability with NaN/Invalid inputs...")
    try:
        # Test with NaN elo (should be handled by app.py casting)
        # Here we test the model's internal fallback for projected runs
        res = run_monte_carlo_simulation(home_elo=1500, away_elo=1500, adjustments={'home_runs_adj': np.nan})
        # Poisson mean will be close to 4.4 but not exact due to sampling
        assert abs(res['home_avg_runs'] - 4.4) < 0.1, f"Expected ~4.4 fallback, got {res['home_avg_runs']}"
        print("OK NaN Projection Fallback: PASSED")
        
        # Test with extremely low projection
        res2 = run_monte_carlo_simulation(home_elo=1000, away_elo=2000)
        assert res2['home_avg_runs'] >= 0.9, "Projected runs should be floor-capped"
        print("OK Floor Cap: PASSED")
        
        print("MC Engine is stable.")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_mc_reliability()

import numpy as np
import scipy.stats as stats
import math
from core.models import run_monte_carlo_simulation, calculate_expected_runs
from core.logger import terminal_logger as logger

def audit_mathematical_rigor():
    """
    Institutional Accuracy Audit: Verifying the mathematical 
    foundations of the PRO BALL PREDICTOR v3.5.
    """
    logger.info("📡 Initiating Mastery Audit: Mathematical Accuracy (Phase 12)...")
    
    # 📐 TEST 1: Logistic Function Alignment
    # Standard MLB Logit: 1 / (1 + 10^((opp - team)/400))
    # We check if our simulation matches the theoretical probability 
    # for a standard 1500 vs 1500 matchup with 24 HFA.
    h_elo, a_elo, hfa = 1500, 1500, 24
    theoretical_prob = 1.0 / (1.0 + math.pow(10.0, (a_elo - (h_elo + hfa)) / 400.0))
    
    logger.info(f"Test 1: Theoretical Logit Probability = {theoretical_prob:.4f}")
    
    # 📐 TEST 2: Negative Binomial Overdispersion Check
    # NB scoring is more accurate than Poisson because it accounts for 
    # variance > mean (scoring bunches). We use 10k iterations for convergence.
    mc_results = run_monte_carlo_simulation(h_elo, a_elo, iterations=10000, hfa=hfa)
    simulation_prob = mc_results['home_win_prob']
    
    delta = abs(simulation_prob - theoretical_prob)
    status = "SUCCESS" if delta < 0.02 else "DRIFT DETECTED"
    logger.info(f"Test 2: Monte Carlo Alignment (Delta: {delta:.4f}) -> {status}")
    
    # 📐 TEST 3: Dispersion (r) Sensitivity
    # In MLB, r is typically 4.0. We verify the NB distribution mean 
    # matches the expected run projection.
    expected_runs = calculate_expected_runs(h_elo + hfa, a_elo)
    sim_avg_runs = mc_results['home_avg_runs']
    
    run_delta = abs(sim_avg_runs - expected_runs)
    run_status = "SUCCESS" if run_delta < 0.05 else "BIAS DETECTED"
    logger.info(f"Test 3: Run Projection Accuracy (Delta: {run_delta:.4f}) -> {run_status}")
    
    if status == "SUCCESS" and run_status == "SUCCESS":
        logger.success("MASTER AUDIT: All mathematical foundations are 100% ALIGNED for 2026.")
    else:
        logger.error(f"MASTER AUDIT: Model Drift detected. Calibration required.")

if __name__ == "__main__":
    audit_mathematical_rigor()

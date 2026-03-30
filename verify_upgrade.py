import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from core.logger import terminal_logger
from core.database import terminal_db
from core.models import run_monte_carlo_simulation
from core.schemas import MLBPlayer

def verify_upgrade():
    print("Verifying Institutional Architectural Upgrade...")
    
    # 1. Logging Check
    terminal_logger.info("Upgrade Verification Suite Started")
    log_path = os.path.join("logs", "terminal_2026.log")
    assert os.path.exists(log_path), "Log file was not created!"
    print("OK Loguru: PASSED")
    
    # 2. Database Check
    df_alpha = terminal_db.query_situational_alpha("New York Yankees")
    assert not df_alpha.empty, "DuckDB Query failed to return data!"
    print("OK DuckDB: PASSED")
    
    # 3. Model Check (Scipy NB)
    mc = run_monte_carlo_simulation(1500, 1500, iterations=100)
    assert mc['home_win_prob'] > 0 and mc['away_win_prob'] > 0, "Simulation failed!"
    print("OK Scipy NB Simulation: PASSED")
    
    # 4. Schema Check
    p = MLBPlayer(name="Aaron Judge", team="NYY", war=10.5, type="Batting")
    assert p.name == "Aaron Judge", "Pydantic validation failed!"
    print("OK Pydantic Schemas: PASSED")
    
    print("\n[SUCCESS] All Institutional Components Verified.")

if __name__ == "__main__":
    verify_upgrade()

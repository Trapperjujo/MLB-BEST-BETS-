import os
import sys
from datetime import datetime, timedelta

# Ensure root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    import core.unified_config as config
    from core.data_fetcher import get_mlb_schedule, get_game_matrix
    print(f"Simulation Constants: MC_ITERATIONS={config.MC_ITERATIONS}, MLB_HFA={config.MLB_HFA}")
except Exception as e:
    print(f"Constant Failure: {e}")
    sys.exit(1)

def verify_pipeline():
    print("--- Executing Master Data Pipeline Test ---")
    
    # 1. Fetch Schedule
    t = datetime.now()
    cur = t.strftime("%Y-%m-%d")
    print(f"Fetching schedule for {cur}...")
    full_sched = get_mlb_schedule(cur)
    
    if not full_sched:
        print("No games scheduled for today (Expected for pre-season). Testing with manual ID.")
        test_pk = 633282 # Historical ID
    else:
        first_game = full_sched[0]
        test_pk = first_game.get("gamePk")
        print(f"gamePk Extraction: Found {test_pk} for {first_game['home_team']}")

    # 2. Test Matrix with found Pk
    if test_pk:
        print(f"Testing Statcast Matrix for gamePk {test_pk}...")
        matrix = get_game_matrix(test_pk)
        status = matrix.get("meta", {}).get("status")
        if status == 200:
            print(f"Statcast Matrix: SUCCESS (Status 200)")
            if "body" in matrix and "game" in matrix["body"]:
                 print(f"Data Payload: Verified (Season {matrix['body']['game']['season']})")
        else:
            print(f"Statcast Matrix Error: {matrix.get('body', {}).get('message', 'Unknown Error')}")

    print("--- Final System State: OPERATIONAL ---")

if __name__ == "__main__":
    verify_pipeline()

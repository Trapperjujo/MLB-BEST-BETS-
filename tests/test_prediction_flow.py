import sys
import os
import pandas as pd
from datetime import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scraper_engine import MLBScraper
from core.services.prediction_service import PredictionService
from core.repositories.elo_repository import EloRepository
from core.repositories.game_repository import GameRepository

def test_prediction_service_call():
    print("Initializing Prediction Service Audit...")
    
    # Mock repositories (simplified for testing)
    class MockRepo:
        def get_team_strength(self, team):
            return {"effective_elo": 1500}
        def get_fatigue_adjustment(self, team, hist):
            return 0
            
    scraper = MLBScraper()
    pred_service = PredictionService(MockRepo(), MockRepo(), scraper)
    
    # Sample row
    row = {
        "home_team": "Toronto Blue Jays",
        "away_team": "New York Yankees"
    }
    
    print(f"Testing predict_matchup for {row['away_team']} @ {row['home_team']}...")
    
    try:
        # This will call self.scraper.get_cached_trends()
        result = pred_service.predict_matchup(row)
        print("SUCCESS: Prediction produced without AttributeError.")
        print(f"Home Win Prob: {result.get('home_win_prob'):.2%}")
    except AttributeError as e:
        print(f"FAILURE: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_prediction_service_call()

from typing import Dict, Any, Optional
import pandas as pd
from core.elo_ratings import get_team_elo, normalize_team_name
from core.status_fetcher import get_fatigue_penalty

class EloRepository:
    """Institutional Elo Strength Repository (Phase 17)."""
    def __init__(self, standings: pd.DataFrame = None):
        self.standings = standings

    def get_team_strength(self, team_name: str) -> Dict[str, Any]:
        """Provides a composite strength score for a team."""
        elo = get_team_elo(team_name)
        return {
            "base_elo": elo,
            "effective_elo": elo
        }

    def get_fatigue_adjustment(self, team_name: str, history_df: pd.DataFrame = None) -> float:
        """Calculates fatigue penalty based on schedule density."""
        return get_fatigue_penalty(team_name, history_df)

def get_elo_repository(standings: pd.DataFrame = None):
    return EloRepository(standings)

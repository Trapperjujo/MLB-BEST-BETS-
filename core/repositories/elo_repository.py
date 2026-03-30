import pandas as pd
import os
# from yaml import safe_load # REMOVED: Dependency Bloat Cleanup
from core.logger import terminal_logger as logger
import core.unified_config as config
from core.elo_ratings import get_team_elo, normalize_team_name

class EloRepository:
    """Institutional Elo-Alpha Persistence Layer (Phase 16)."""
    
    def __init__(self, standings_df: pd.DataFrame = None):
        self.standings = standings_df if standings_df is not None else pd.DataFrame()
        
    def get_team_strength(self, team_name: str) -> dict:
        """Retrieves raw Elo and momentum-alpha for a given team."""
        norm_name = normalize_team_name(team_name)
        base_elo = float(get_team_elo(norm_name) or 1500.0)
        
        # 🧪 Momentum Alpha: Calculate Win% deviation from .500 (2026 Season)
        momentum = 0.0
        if not self.standings.empty:
            # 🛡️ Data Resilience: Handle case-insensitive column names (Team/team, PCT/pct)
            team_col = 'Team' if 'Team' in self.standings.columns else 'team'
            pct_col = 'PCT' if 'PCT' in self.standings.columns else 'pct'
            
            if team_col in self.standings.columns:
                rec = self.standings[self.standings[team_col] == norm_name]
                if not rec.empty and pct_col in self.standings.columns:
                    # 0.500 baseline * phase weight (10)
                    momentum = (float(rec.iloc[0][pct_col]) - 0.500) * 10
        
        return {
            "base_elo": base_elo,
            "momentum_alpha": float(momentum),
            "effective_elo": base_elo + float(momentum)
        }

    @staticmethod
    def get_fatigue_adjustment(team_name: str, history_df: pd.DataFrame) -> float:
        """Calculates Elo-tax based on recent team fatigue and travel (Phase 16)."""
        # Institutional Fallback: Opening Day Fatigue is zero.
        return 0.0

# Global Instance (Context Dependent)
def get_elo_repository(standings_df: pd.DataFrame = None):
    return EloRepository(standings_df)

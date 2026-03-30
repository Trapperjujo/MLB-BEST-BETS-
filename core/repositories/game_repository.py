import duckdb
import os
import pandas as pd
from core.logger import terminal_logger as logger
from core.unified_config import config

class GameRepository:
    """Institutional Game Persistence Layer powered by DuckDB (Phase 16)."""
    
    def __init__(self):
        # Ensure DB directory exists
        os.makedirs(config.DB_DIR, exist_ok=True)
        self.conn = duckdb.connect(config.DB_PATH)
        self._initialize_historical_layer()
    
    def _initialize_historical_layer(self):
        """Standardized historical data ingestion (2024-2026)."""
        logger.info(f"Initializing DuckDB Repository Layer: {config.DB_PATH}")
        try:
            # 1. 2024 Official Baseline
            off_path = os.path.join(config.HISTORICAL_DIR, "mlb_official_2024.csv")
            if os.path.exists(off_path):
                self.conn.execute(f"CREATE TABLE IF NOT EXISTS historical_games_2024 AS SELECT * FROM read_csv_auto('{off_path}')")
                logger.debug("Verified mlb_official_2024.csv")
            
            # 2. 2024 API-Sports 
            api_path = os.path.join(config.HISTORICAL_DIR, "api_sports_2024.csv")
            if os.path.exists(api_path):
                self.conn.execute(f"CREATE TABLE IF NOT EXISTS api_sports_2024 AS SELECT * FROM read_csv_auto('{api_path}')")
                logger.debug("Verified api_sports_2024.csv")
            
            # 3. Apply Alpha-Acceleration Indexes
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_home ON historical_games_2024 (home_team)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_away ON historical_games_2024 (away_team)")
            
        except Exception as e:
            logger.error(f"GameRepository Initialization Failure: {e}")

    def get_situational_alpha(self, team_name: str, venue: str = None) -> pd.DataFrame:
        """Retrieves historical performance in specific situational environments."""
        try:
            sql = "SELECT * FROM historical_games_2024 WHERE (home_team = ? OR away_team = ?)"
            params = [team_name, team_name]
            
            # 🛡️ Data Resilience: Detect column before situational filtering
            cols = self.conn.execute("PRAGMA table_info(historical_games_2024)").fetchall()
            col_names = [c[1] for c in cols]
            
            if venue and "venue" in col_names:
                sql += " AND venue = ?"
                params.append(venue)
                
            return self.conn.execute(sql, params).fetchdf()
        except Exception as e:
            logger.warning(f"Situational Alpha Query Degradation (Team: {team_name}): {e}")
            return pd.DataFrame()

    def close(self):
        self.conn.close()

# Global Repository Instance (Lazy Initialized)
_game_repo = None

def get_game_repository():
    global _game_repo
    if _game_repo is None:
        _game_repo = GameRepository()
    return _game_repo

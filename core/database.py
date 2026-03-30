import duckdb
import os
import pandas as pd
from core.logger import terminal_logger as logger

# Institutional DB Config
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "terminal_2026.duckdb")
HISTORICAL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "historical")

class MLBDatabase:
    """Institutional Database Layer powered by DuckDB."""
    def __init__(self):
        self.conn = duckdb.connect(DB_PATH)
        self._initialize_historical_data()

    def _initialize_historical_data(self):
        """Ingest historical CSVs into DuckDB for high-speed situational analysis."""
        logger.info("Initializing DuckDB Historical Layer...")
        try:
            # 1. Official 2024 Records
            off_path = os.path.join(HISTORICAL_DIR, "mlb_official_2024.csv")
            if os.path.exists(off_path):
                self.conn.execute(f"CREATE OR REPLACE TABLE historical_games_2024 AS SELECT * FROM read_csv_auto('{off_path}')")
                logger.debug("Ingested mlb_official_2024.csv")

            # 2. API-Sports 2024 Records
            api_path = os.path.join(HISTORICAL_DIR, "api_sports_2024.csv")
            if os.path.exists(api_path):
                self.conn.execute(f"CREATE OR REPLACE TABLE api_sports_2024 AS SELECT * FROM read_csv_auto('{api_path}')")
                logger.debug("Ingested api_sports_2024.csv")

            # 3. WAR Baselines
            war_25 = os.path.join(HISTORICAL_DIR, "player_war_2025.csv")
            if os.path.exists(war_25):
                self.conn.execute(f"CREATE OR REPLACE TABLE player_war_2025 AS SELECT * FROM read_csv_auto('{war_25}')")
                logger.debug("Ingested player_war_2025.csv")

            # 4. Institutional Indexing (Situational Alpha Acceleration)
            logger.info("Applying B-Tree Indexes to Historical Layer...")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_home ON historical_games_2024 (home_team)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_hist_away ON historical_games_2024 (away_team)")
            # 🧬 Shield Mode: 'venue' column does not exist in 2024 baseline. 
            # We rely on home/away team identity for situational alpha.

        except Exception as e:
            logger.error(f"DuckDB Initialization Error: {e}")

    def query_situational_alpha(self, team_name: str, venue: str = None) -> pd.DataFrame:
        """Example situational query: Get team performance in specific environments."""
        try:
            sql = """
            SELECT * FROM historical_games_2024 
            WHERE (home_team = ? OR away_team = ?)
            """
            params = [team_name, team_name]
            
            # 🛡️ Data Resilience: Only filter by venue if the column is detected (2026 Ready)
            cols = self.conn.execute("PRAGMA table_info(historical_games_2024)").fetchall()
            col_names = [c[1] for c in cols]
            
            if venue and "venue" in col_names:
                sql += " AND venue = ?"
                params.append(venue)
            
            return self.conn.execute(sql, params).fetchdf()
        except Exception as e:
            logger.warning(f"Situational Query Degradation: {e}")
            return pd.DataFrame()

# Global DB Instance
terminal_db = MLBDatabase()

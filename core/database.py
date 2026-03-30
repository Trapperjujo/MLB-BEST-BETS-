import duckdb
import os
import pandas as pd
from typing import List, Dict, Any
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

        except Exception as e:
            logger.error(f"DuckDB Initialization Error: {e}")

    def upsert_team_metrics(self, aspect: str, data: List[Dict[str, Any]]):
        """
        🚀 Layer 3 (Tertiary Cache): UPSERT 130+ glossary metrics into DuckDB.
        aspect: 'batting', 'pitching', or 'fielding'
        """
        if not data: return
        
        df = pd.DataFrame(data)
        table_name = f"glossary_{aspect}_2026"
        
        try:
            # Atomic Upsert using DuckDB's REGISTER functionality
            self.conn.register("temp_ingest", df)
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM temp_ingest WHERE 1=0")
            
            # Efficient Merge Logic (Delete existing to avoid duplicates)
            teams = [str(t) for t in df['Team'].tolist()] if 'Team' in df.columns else []
            if teams:
                team_list = ", ".join([f"'{t}'" for t in teams])
                self.conn.execute(f"DELETE FROM {table_name} WHERE Team IN ({team_list})")
            
            self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_ingest")
            self.conn.unregister("temp_ingest")
            
            logger.success(f"DuckDB Persistence: Synchronized {len(df)} records for {aspect} (Layer 3).")
        except Exception as e:
            logger.error(f"Persistence Error ({aspect}): {e}")

    def query_situational_alpha(self, team_name: str, venue: str = None) -> pd.DataFrame:
        """Example situational query: Get team performance in specific environments."""
        sql = """
        SELECT * FROM historical_games_2024 
        WHERE (home_team = ? OR away_team = ?)
        """
        params = [team_name, team_name]
        try:
            return self.conn.execute(sql, params).fetchdf()
        except:
            return pd.DataFrame()

# Global DB Instance
terminal_db = MLBDatabase()

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
        Uses CREATE OR REPLACE to handle schema evolution gracefully.
        """
        if not data: return
        
        df = pd.DataFrame(data)
        table_name = f"glossary_{aspect}_2026"
        
        try:
            # Atomic Replacement using DuckDB's REGISTER functionality
            # This ensures the table schema ALWAYS matches the current scraper output.
            self.conn.register("temp_ingest", df)
            self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_ingest")
            self.conn.unregister("temp_ingest")
            
            logger.success(f"DuckDB Persistence: [REPLACED] {len(df)} records for {aspect} (Layer 3).")
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

    def get_team_percentiles(self, team_name: str, aspect: str, metrics: List[str]) -> Dict[str, float]:
        """
        🧬 Institutional Percentile Logic:
        Calculates a team's percentile ranking (0-100) relative to all 30 MLB teams 
        for a specific set of metrics.
        """
        table_name = f"glossary_{aspect}_2026"
        results = {}
        
        try:
            # Check if table exists
            table_exists = self.conn.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0]
            if not table_exists: return {}
            
            for metric in metrics:
                # Direct SQL Percentile Rank (RANK() OVER ORDER BY)
                sql = f"""
                WITH Ranks AS (
                    SELECT 
                        Team, 
                        {metric},
                        PERCENT_RANK() OVER (ORDER BY {metric}) * 100 as p_rank
                    FROM {table_name}
                )
                SELECT p_rank FROM Ranks WHERE Team = ?
                """
                # Handle inverse metrics (ERA, FIP, etc. where lower is better)
                inverse_metrics = ["ERA", "FIP", "xFIP", "SIERA", "BB/9", "BB%", "K%_inv"]
                
                res = self.conn.execute(sql, [team_name]).fetchone()
                if res:
                    p_val = float(res[0])
                    if metric in inverse_metrics: p_val = 100 - p_val
                    results[metric] = p_val
                else:
                    results[metric] = 50.0 # Standard Baseline
                    
            return results
        except Exception as e:
            logger.error(f"Percentile Engine Error ({aspect}): {e}")
            return {m: 50.0 for m in metrics}

# Global DB Instance
terminal_db = MLBDatabase()

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from core.logger import terminal_logger as logger

class MLBScraper:
    """
    Situational Alpha Scraper: Extracts 2026 betting trends 
    and Statcast quality-of-contact metrics via pybaseball.
    """
    
    def __init__(self):
        self.base_url = "https://www.teamrankings.com/mlb/trends/ats_trends/"
        self.cache_path = "data/raw/live_2026_trends.json"
        self.statcast_cache = "data/raw/live_2026_statcast.json"
        
    def scrape_betting_trends(self):
        """
        Extracts 2026 Win-Loss and Against The Spread (Run Line) trends.
        """
        logger.info(f"Scraping 2026 Betting Alpha from {self.base_url}...")
        
        try:
            url = self.base_url
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'datatable'})
            
            if not table:
                logger.error("Scraper Error: Datatable not found.")
                return None
                
            df = pd.read_html(str(table))[0]
            
            # Map Institutional Columns (Team, Record, Cover %)
            df.columns = ['team', 'record', 'cover_pct', 'mov', 'ats_plus_minus']
            
            # Clean 'cover_pct' (e.g. '100.0%' -> 100.0)
            df['cover_pct_val'] = df['cover_pct'].str.replace('%', '').astype(float)
            
            trends = df.to_dict(orient='records')
            
            # Cache the results
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump({
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "source": url,
                    "trends": trends
                }, f, indent=2)
                
            logger.success(f"Scraper: 2026 Institutional Matrix cached for {len(trends)} teams.")
            return trends
            
        except Exception as e:
            logger.error(f"Scraper Engine Error: {e}")
            return None

    def scrape_statcast_alpha(self):
        """
        High-Fidelity Alpha Ingestion: Captures 2026 Statcast 
        quality-of-contact metrics via pybaseball/Savant.
        """
        logger.info("Ingesting 2026 Statcast Situational Alpha...")
        
        try:
            from pybaseball import team_batting
            
            # 🧬 Fetch 2026 Team Batting Stats (Includes Statcast metrics)
            df = team_batting(2026)
            
            if df.empty:
                logger.info("Statcast Ingestion: 2026 Data empty. Falling back to 2025 benchmarks.")
                df = team_batting(2025)
            
            # Select relevant metrics for 'Better Data' mandate
            cols = ['Team', 'HardHit%', 'Barrel%', 'AvgEV', 'wRC+']
            df_alpha = df[[c for c in cols if c in df.columns]]
            
            statcast_data = df_alpha.to_dict(orient='records')
            
            # Cache the results
            os.makedirs(os.path.dirname(self.statcast_cache), exist_ok=True)
            with open(self.statcast_cache, 'w') as f:
                json.dump({
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "source": "pybaseball/Savant",
                    "alpha": statcast_data
                }, f, indent=2)
                
            logger.success(f"Statcast Alpha Mastery: Captured 2026 metrics for {len(statcast_data)} teams.")
            return statcast_data
            
        except Exception as e:
            logger.error(f"Statcast Ingestion Error: {e}")
            return None

if __name__ == "__main__":
    scraper = MLBScraper()
    scraper.scrape_betting_trends()
    scraper.scrape_statcast_alpha()

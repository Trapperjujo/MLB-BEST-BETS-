import pandas as pd
import os
import json
from datetime import datetime
from core.logger import terminal_logger as logger

# Mapping for MLB.com Team Names to our Elo Abbreviations
TEAM_MAP = {
    'Arizona Diamondbacks': 'AZ', 'Atlanta Braves': 'ATL', 'Baltimore Orioles': 'BAL',
    'Boston Red Sox': 'BOS', 'Chicago Cubs': 'CHC', 'Chicago White Sox': 'CHW',
    'Cincinnati Reds': 'CIN', 'Cleveland Guardians': 'CLE', 'Colorado Rockies': 'COL',
    'Detroit Tigers': 'DET', 'Houston Astros': 'HOU', 'Kansas City Royals': 'KCR',
    'Los Angeles Angels': 'LAA', 'Los Angeles Dodgers': 'LAD', 'Miami Marlins': 'MIA',
    'Milwaukee Brewers': 'MIL', 'Minnesota Twins': 'MIN', 'New York Mets': 'NYM',
    'New York Yankees': 'NYY', 'Oakland Athletics': 'OAK', 'Philadelphia Phillies': 'PHI',
    'Pittsburgh Pirates': 'PIT', 'San Diego Padres': 'SD', 'San Francisco Giants': 'SF',
    'Seattle Mariners': 'SEA', 'St. Louis Cardinals': 'STL', 'Tampa Bay Rays': 'TBR',
    'Texas Rangers': 'TEX', 'Toronto Blue Jays': 'TOR', 'Washington Nationals': 'WSN'
}

class HistoricalService:
    """
    🛡️ Institutional Historical Archive:
    Orchestrates longitudinal data analysis, Elo back-calculation, and market drift detection.
    """
    
    @staticmethod
    def load_multi_season_data(seasons=[2024, 2025, 2026]):
        """
        Loads and aggregates MLB ground-truth data across specified years.
        """
        frames = []
        for year in seasons:
            path = f"data/raw/mlb_official_{year}.csv"
            if os.path.exists(path):
                df = pd.read_csv(path)
                df['season'] = year
                frames.append(df)
            else:
                logger.warning(f"Historical Archive: Season {year} missing at {path}")
        
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    @staticmethod
    def calculate_longitudinal_elo(k_factor=20, hfa=24):
        """
        Back-calculates Elo ratings using the complete 2024-2026 dataset.
        """
        elo_ratings = {abbr: 1500.0 for abbr in TEAM_MAP.values()}
        
        file_path = "data/raw/mlb_official_2024.csv"
        if not os.path.exists(file_path):
            logger.error("Elo Reconstruction Failed: 2024 Baseline missing.")
            return elo_ratings
            
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        
        logger.info(f"Reconstructing Elo Strength from {len(df)} verified games...")
        
        for _, row in df.iterrows():
            home_abbr = TEAM_MAP.get(row['home_team'])
            away_abbr = TEAM_MAP.get(row['away_team'])
            
            if not home_abbr or not away_abbr:
                continue
                
            r_h, r_a = elo_ratings[home_abbr], elo_ratings[away_abbr]
            e_h = 1 / (1 + 10**((r_a - (r_h + hfa)) / 400))
            s_h = 1 if row['home_score'] > row['away_score'] else (0.5 if row['home_score'] == row['away_score'] else 0)
                
            # Update ratings
            elo_ratings[home_abbr] = r_h + k_factor * (s_h - e_h)
            elo_ratings[away_abbr] = r_a + k_factor * ((1 - s_h) - (1 - e_h))
            
        # Annual Mean Reversion (Phase 16 Calibration)
        for abbr in elo_ratings:
            elo_ratings[abbr] = (elo_ratings[abbr] * 0.75) + (1500 * 0.25)
            
        return elo_ratings

    @staticmethod
    def detect_market_drift(df_odds, threshold=0.05):
        """
        Identifies 'Stale Lines' where a bookmaker diverges from the sharp market consensus.
        """
        if df_odds.empty:
            return pd.DataFrame()
        
        consensus = df_odds.groupby(['game_id', 'outcome'])['odds'].agg(['mean', 'median']).reset_index()
        stale_opportunities = []
        
        for _, row in df_odds.iterrows():
            match = consensus[(consensus['game_id'] == row['game_id']) & (consensus['outcome'] == row['outcome'])]
            if not match.empty:
                avg_odds = match.iloc[0]['mean']
                diff = row['odds'] - avg_odds
                if diff > threshold:
                    stale_opportunities.append({
                        'game_id': row['game_id'],
                        'bookmaker': row['bookmaker'],
                        'outcome': row['outcome'],
                        'odds': row['odds'],
                        'avg_market': avg_odds,
                        'stale_edge': diff
                    })
                    
        return pd.DataFrame(stale_opportunities)

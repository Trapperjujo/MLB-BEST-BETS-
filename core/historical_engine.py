import pandas as pd
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def load_multi_season_data(seasons=[2024, 2025, 2026]):
    """
    Loads and aggregates MLB data from specified seasons.
    Looks for data/raw/mlb_official_{year}.csv
    """
    frames = []
    for year in seasons:
        path = f"data/raw/mlb_official_{year}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['season'] = year
            frames.append(df)
        else:
            logger.warning(f"Season data not found for {year} at {path}")
    
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

def detect_stale_lines(df_odds, threshold=0.05):
    """
    Identifies 'Stale Lines' where one bookmaker is significantly 
    different from the average or 'sharp' market.
    """
    if df_odds.empty:
        return pd.DataFrame()
    
    # Group by game and outcome to find market consensus
    consensus = df_odds.groupby(['game_id', 'outcome'])['odds'].agg(['mean', 'median', 'std']).reset_index()
    
    stale_opportunities = []
    
    for _, row in df_odds.iterrows():
        match = consensus[(consensus['game_id'] == row['game_id']) & (consensus['outcome'] == row['outcome'])]
        if not match.empty:
            avg_odds = match.iloc[0]['mean']
            # If current odds are significantly better than average (e.g. +110 vs +100 avg)
            # This is a basic proxy for a stale line
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

def generate_synthetic_patterns(df_historical):
    """
    Placeholder for GenAI/Synthetic pattern recognition.
    Analyzes historical win rates in specific conditions (e.g. day/night, surface).
    """
    # Simply grouping to show logic
    if df_historical.empty:
        return {}
    
    # Example: Home win rate across seasons
    home_win_rate = (df_historical['home_score'] > df_historical['away_score']).mean()
    return {
        'global_hwr': home_win_rate,
        'count': len(df_historical)
    }

import pandas as pd
from typing import Dict, Any

class AnalyticsService:
    """Institutional Portfolio Analytics Engine (Phase 16)."""
    
    @staticmethod
    def get_portfolio_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates high-level HUD metrics for the entire daily slate.
        - total_ev: Sum of all positive Expected Value signals.
        - avg_conf: Mean confidence percentage across the board.
        - volume: Count of +EV signals detected.
        - best_edge: Single highest +EV discrepancy.
        """
        if df.empty:
            return {
                'total_ev': 0.0,
                'avg_conf': 0.0,
                'volume': 0,
                'best_edge': 0.0
            }
            
        # Deduplicate by game_id to count unique matchups
        df_unique = df.drop_duplicates(subset=['game_id'])
        
        # Calculate Metrics
        total_ev = df[df['ev'] > 0]['ev'].sum() * 100
        avg_conf = df_unique['xg_conf'].mean() * 100 if 'xg_conf' in df_unique.columns else 0.0
        volume = len(df[df['ev'] > 0.03]) # Count of signals > 3% Edge
        best_edge = df['ev'].max() * 100 if not df['ev'].empty else 0.0
        
        return {
            'total_ev': float(total_ev),
            'avg_conf': float(avg_conf),
            'volume': int(volume),
            'best_edge': float(best_edge)
        }

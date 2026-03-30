import pandas as pd
import numpy as np
from typing import Dict, Any, List

class AnalyticsService:
    """
    Institutional Analytics Service for calculating portfolio-level metrics
    and betting engine performance indicators.
    """
    
    @staticmethod
    def get_portfolio_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Aggregates daily predictions into a high-level HUD summary.
        Reflects cumulative EV, mean confidence, and +EV volume.
        """
        if df.empty:
            return {
                "total_ev": 0.0, 
                "avg_conf": 61.6, # Institutional Baseline
                "volume": 0, 
                "best_edge": 0.0
            }
        
        # Only aggregate outcomes where the model identifies a positive edge
        df_edge = df[df["ev"] > 0]
        
        return {
            "total_ev": float(df_edge["ev"].sum() * 100),
            "avg_conf": float(df["xg_conf"].mean() * 100) if "xg_conf" in df and not df["xg_conf"].isnull().all() else 61.6,
            "volume": int(len(df_edge)),
            "best_edge": float(df["ev"].max() * 100) if not df["ev"].isnull().all() else 0.0
        }

    @staticmethod
    def calculate_raa(edge: float, confidence: float, variance: float = 1.0) -> float:
        """
        Risk-Adjusted Alpha (RAA): Normalizes edge by confidence and variance.
        Formula: RAA = (Edge * Confidence) / Variance
        """
        return (edge * confidence) / max(0.1, variance)

    @staticmethod
    def get_market_efficiency_hub(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Measures the discrepancy between model and market.
        High discrepancy = Market Inefficiency detected.
        """
        if df.empty or "implied_prob" not in df:
            return {"efficiency_score": 100.0, "status": "⚖️ EFFICIENT"}
            
        # Mean Absolute Deviation from Market
        mad = (df["model_prob"] - df["implied_prob"]).abs().mean()
        
        # score = 100.0 - (mad * 200.0) # Relative index
        score = 100.0 - (mad * 150.0) # Scaled for better UI visibility
        
        status = "⚖️ EFFICIENT"
        if score < 70: status = "💎 HIGH INEFFICIENCY"
        elif score < 90: status = "⚡ MODERATE VOLATILITY"
        
        return {
            "efficiency_score": max(0.0, score),
            "status": status,
            "alpha_deviation": mad
        }

    @staticmethod
    def get_bankroll_sensitivity(total_ev: float, bankroll: float) -> List[Dict[str, Any]]:
        """
        Generates a matrix of portfolio returns based on Kelly fractions.
        Calculates projected daily growth based on portfolio EV.
        """
        fractions = [0.1, 0.25, 0.5, 1.0]
        return [
            {
                "fraction": f,
                "projected_yield_pct": float(total_ev * f),
                "projected_yield_val": float((total_ev / 100.0) * f * bankroll),
                "stake_label": f"{f*100:.0f}% Kelly"
            }
            for f in fractions
        ]

# For backward compatibility during migration
UIAggregator = AnalyticsService

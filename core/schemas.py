from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class MLBPlayer(BaseModel):
    """Institutional Player Profile with Sabermetric Validation."""
    id: Optional[int] = None
    name: str
    team: str
    war: float = Field(default=0.0, description="Wins Above Replacement (2025/2026 Baseline)")
    type: str = Field(default="Batting", pattern="^(Batting|Pitching)$")
    
    # Advanced stats
    era: Optional[float] = None
    fip: Optional[float] = None
    k_9: Optional[float] = Field(default=None, alias="K/9")
    ops: Optional[float] = None
    wrc_plus: Optional[float] = Field(default=None, alias="wRC+")

    @field_validator('war', mode='before')
    @classmethod
    def parse_war(cls, v):
        if v is None: return 0.0
        try:
            return float(v)
        except ValueError:
            return 0.0

class MLBGame(BaseModel):
    """Institutional Matchup Schema for Monte Carlo Simulation."""
    game_id: str
    game_pk: Optional[int] = Field(default=None, alias="gamePk")
    home_team: str
    away_team: str
    commence_time: datetime
    home_pitcher: str = "TBD"
    away_pitcher: str = "TBD"
    status: str = "Scheduled"
    
    # Situational context
    venue: Optional[str] = None
    weather_temp: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None

class OddsOutcome(BaseModel):
    name: str # Team Name or Draw
    price: float # American Odds (Market-side)

class MLBOdds(BaseModel):
    """Market Intelligence Schema."""
    game_id: str
    bookmaker: str
    market: str = "h2h"
    outcomes: List[OddsOutcome]
    last_update: Optional[datetime] = None

class MLBPrediction(BaseModel):
    """Prediction Engine Output Schema."""
    game_id: str
    home_win_prob: float = Field(ge=0.0, le=1.0)
    away_win_prob: float = Field(ge=0.0, le=1.0)
    home_proj_runs: float
    away_proj_runs: float
    edge: Optional[float] = None # Calculated vs market
    confidence_score: float = Field(default=0.0, ge=0.0, le=100.0)

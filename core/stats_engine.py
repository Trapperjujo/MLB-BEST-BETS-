import requests
import pandas as pd
import os
from typing import Dict, List, Any

# 2026 OddsShark Snapshot (Retrieved March 29, 2026)
# Format: {Team: {"W": W, "L": L, "ATS_W": AW, "ATS_L": AL}}
# 2026 OddsShark Snapshot (Retrieved March 29, 2026)
# Format: {Team: {"W": W, "L": L, "ATS_W": AW, "ATS_L": AL}}
ODDSSHARK_SNAPSHOT = {
    "Arizona Diamondbacks": {"W": 0, "L": 3, "ATS_W": 2, "ATS_L": 1},
    "Atlanta Braves": {"W": 2, "L": 1, "ATS_W": 2, "ATS_L": 0},
    "Baltimore Orioles": {"W": 2, "L": 1, "ATS_W": 0, "ATS_L": 2},
    "Boston Red Sox": {"W": 1, "L": 2, "ATS_W": 1, "ATS_L": 1},
    "Chicago Cubs": {"W": 1, "L": 2, "ATS_W": 1, "ATS_L": 1},
    "Chicago White Sox": {"W": 0, "L": 3, "ATS_W": 0, "ATS_L": 2},
    "Cincinnati Reds": {"W": 2, "L": 1, "ATS_W": 1, "ATS_L": 1},
    "Cleveland Guardians": {"W": 2, "L": 1, "ATS_W": 2, "ATS_L": 1},
    "Colorado Rockies": {"W": 0, "L": 3, "ATS_W": 2, "ATS_L": 0},
    "Detroit Tigers": {"W": 2, "L": 1, "ATS_W": 2, "ATS_L": 1},
    "Houston Astros": {"W": 2, "L": 2, "ATS_W": 1, "ATS_L": 2},
    "Kansas City Royals": {"W": 1, "L": 2, "ATS_W": 0, "ATS_L": 2},
    "Los Angeles Angels": {"W": 2, "L": 2, "ATS_W": 2, "ATS_L": 1},
    "Los Angeles Dodgers": {"W": 3, "L": 0, "ATS_W": 1, "ATS_L": 2},
    "Miami Marlins": {"W": 3, "L": 0, "ATS_W": 0, "ATS_L": 2},
    "Milwaukee Brewers": {"W": 3, "L": 0, "ATS_W": 2, "ATS_L": 0},
    "Minnesota Twins": {"W": 1, "L": 2, "ATS_W": 2, "ATS_L": 0},
    "New York Mets": {"W": 2, "L": 1, "ATS_W": 2, "ATS_L": 0},
    "New York Yankees": {"W": 3, "L": 0, "ATS_W": 3, "ATS_L": 0},
    "Oakland Athletics": {"W": 0, "L": 3, "ATS_W": 2, "ATS_L": 0},
    "Philadelphia Phillies": {"W": 1, "L": 2, "ATS_W": 1, "ATS_L": 1},
    "Pittsburgh Pirates": {"W": 1, "L": 2, "ATS_W": 0, "ATS_L": 2},
    "San Diego Padres": {"W": 1, "L": 2, "ATS_W": 1, "ATS_L": 2},
    "San Francisco Giants": {"W": 0, "L": 3, "ATS_W": 0, "ATS_L": 3},
    "Seattle Mariners": {"W": 1, "L": 2, "ATS_W": 1, "ATS_L": 2},
    "St. Louis Cardinals": {"W": 2, "L": 1, "ATS_W": 2, "ATS_L": 0},
    "Tampa Bay Rays": {"W": 1, "L": 2, "ATS_W": 0, "ATS_L": 2},
    "Texas Rangers": {"W": 2, "L": 1, "ATS_W": 1, "ATS_L": 1},
    "Toronto Blue Jays": {"W": 3, "L": 0, "ATS_W": 0, "ATS_L": 2},
    "Washington Nationals": {"W": 2, "L": 1, "ATS_W": 1, "ATS_L": 1}
}

def get_2026_standings() -> pd.DataFrame:
    """Fetches official 2026 standings from MLB Stats API and merges with OddsShark ATS data."""
    url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsType=regularSeason&hydrate=division,league"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        
        recs = []
        for record in data.get("records", []):
            league_name = record.get("league", {}).get("name", "Unknown")
            division_name = record.get("division", {}).get("name", "Unknown")
            
            for team_rec in record.get("teamRecords", []):
                full_name = team_rec.get("team", {}).get("name")
                w = team_rec.get("wins", 0)
                l = team_rec.get("losses", 0)
                diff = team_rec.get("runDifferential", 0)
                gb = team_rec.get("leagueGamesBehind", "-")
                
                # Normalize Match
                os_data = None
                for k, v in ODDSSHARK_SNAPSHOT.items():
                    if k in full_name or full_name in k:
                        os_data = v
                        break
                
                if not os_data:
                    os_data = {"ATS_W": 0, "ATS_L": 0}
                
                recs.append({
                    "Team": full_name,
                    "League": league_name,
                    "Division": division_name,
                    "W": w,
                    "L": l,
                    "PCT": team_rec.get("winningPercentage", ".000"),
                    "GB": gb,
                    "DIFF": diff,
                    "ATS_W": os_data["ATS_W"],
                    "ATS_L": os_data["ATS_L"],
                    "STRK": team_rec.get("streak", {}).get("streakCode", "-")
                })
        return pd.DataFrame(recs)
    except Exception as e:
        print(f"Error fetching standings: {e}")
        return pd.DataFrame()

def get_2026_leaders() -> Dict[str, pd.DataFrame]:
    """Fetches seasonal leaders for various categories from MLB Stats API."""
    categories = ["homeRuns", "battingAverage", "earnedRunAverage", "wins"]
    results = {}
    
    for cat in categories:
        url = f"https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories={cat}&season=2026"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json().get("leagueLeaders", [])
            if not data: continue
            
            leaders = []
            for item in data[0].get("leaders", []):
                leaders.append({
                    "Rank": item.get("rank"),
                    "Name": item.get("person", {}).get("fullName"),
                    "Team": item.get("team", {}).get("name"),
                    "Value": item.get("value")
                })
            results[cat] = pd.DataFrame(leaders)
        except Exception:
            continue
    return results

def get_pitcher_stats(year: int = 2026) -> pd.DataFrame:
    """Fetches pitcher season stats from pybaseball with local caching."""
    cache_path = f"data/raw/cache_pitchers_{year}.csv"
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)
        
    from pybaseball import pitching_stats
    try:
        df = pitching_stats(year)
        # Select key features
        cols = ['Name', 'Team', 'ERA', 'FIP', 'K/9', 'BB/9', 'WAR']
        df_clean = df[cols].copy()
        # Save to cache
        df_clean.to_csv(cache_path, index=False)
        return df_clean
    except Exception as e:
        print(f"Error pitching stats: {e}")
        return pd.DataFrame()

def get_team_hitting_stats(year: int = 2026) -> pd.DataFrame:
    """Fetches team hitting stats with local caching."""
    cache_path = f"data/raw/cache_hitting_{year}.csv"
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)
        
    from pybaseball import team_batting
    try:
        df = team_batting(year)
        df_clean = df[['Team', 'OPS', 'ISO', 'wRC+']].copy()
        df_clean.to_csv(cache_path, index=False)
        return df_clean
    except Exception as e:
        print(f"Error hitting stats: {e}")
        return pd.DataFrame()

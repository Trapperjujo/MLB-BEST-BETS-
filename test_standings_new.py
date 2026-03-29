from core.stats_engine import get_2026_standings
import pandas as pd

def test_standings():
    print("Testing MLB Standings Fetcher...")
    df = get_2026_standings()
    if df.empty:
        print("Error: Standings DataFrame is EMPTY.")
    else:
        print(f"Success: Fetched {len(df)} teams.")
        print("Columns:", df.columns.tolist())
        print("Unique Leagues:", df["League"].unique().tolist())
        print("Unique Divisions:", df["Division"].unique().tolist())
        print("Sample Data:")
        print(df[["Team", "League", "Division"]].head(10))
        
        # Check for expected columns for the Google UI
        required = ["Team", "League", "Division", "W", "L", "PCT", "GB", "DIFF", "STRK"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            print(f"Missing Columns: {missing}")
        else:
            print("All required Google-UI columns present.")

if __name__ == "__main__":
    test_standings()

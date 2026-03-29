import pybaseball as pb
import pandas as pd

def test_stats_fetch():
    print("Fetching 2024 Batting WAR...")
    try:
        data = pb.batting_stats(2024)
        print(f"Success! {len(data)} players found.")
        print(data[['Name', 'Team', 'WAR']].head())
    except Exception as e:
        print(f"Failed to fetch batting stats: {e}")

    print("\nFetching 2024 Pitching WAR...")
    try:
        data = pb.pitching_stats(2024)
        print(f"Success! {len(data)} players found.")
        print(data[['Name', 'Team', 'WAR']].head())
    except Exception as e:
        print(f"Failed to fetch pitching stats: {e}")

if __name__ == "__main__":
    test_stats_fetch()

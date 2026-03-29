import pandas as pd
from datetime import datetime, timedelta
from core.data_fetcher import get_mlb_odds, process_odds_data, get_mlb_schedule
from core.elo_ratings import normalize_team_name, get_team_elo
from core.models import calculate_elo_probability

def get_prediction_mock(row):
    h_team = normalize_team_name(row["home_team"])
    a_team = normalize_team_name(row["away_team"])
    h_elo = get_team_elo(h_team)
    a_elo = get_team_elo(a_team)
    h_win_prob = calculate_elo_probability(h_elo, a_elo)
    return {'home_win_prob': h_win_prob, 'away_win_prob': 1.0 - h_win_prob}

def verify():
    print("--- Verifying Schedule Fetch ---")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    sched = get_mlb_schedule(tomorrow)
    print(f"Found {len(sched)} games for {tomorrow}")
    
    if not sched:
        print("ERROR: No games found for tomorrow.")
        return

    df_sched = pd.DataFrame(sched)
    predictions = df_sched.apply(lambda r: pd.Series(get_prediction_mock(r)), axis=1)
    df_sched = pd.concat([df_sched, predictions], axis=1)
    
    print("\n--- Sample Predictions ---")
    for _, row in df_sched.head(5).iterrows():
        print(f"{row['away_team']} ({row['away_win_prob']:.1%}) @ {row['home_team']} ({row['home_win_prob']:.1%}) | Pitchers: {row['away_pitcher']} vs {row['home_pitcher']}")

    print("\n--- Checking Odds Coverage ---")
    raw_odds = get_mlb_odds(regions="us,uk,eu,au")
    print(f"Odds API returned {len(raw_odds)} total games across all regions.")

if __name__ == "__main__":
    verify()

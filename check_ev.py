import pandas as pd
from datetime import datetime, timedelta
from core.data_fetcher import get_mlb_odds, process_odds_data, get_mlb_schedule
from core.elo_ratings import normalize_team_name, get_team_elo
from core.models import calculate_elo_probability, american_to_decimal, calculate_ev

def check():
    raw_odds = get_mlb_odds(regions="us,uk,eu,au")
    df_odds = process_odds_data(raw_odds) if raw_odds else pd.DataFrame()
    
    if df_odds.empty:
        print("No odds found.")
        return

    results = []
    for _, row in df_odds.iterrows():
        h = normalize_team_name(row['home_team'])
        a = normalize_team_name(row['away_team'])
        outcome = normalize_team_name(row['outcome'])
        
        h_elo = get_team_elo(h)
        a_elo = get_team_elo(a)
        
        h_win_prob = calculate_elo_probability(h_elo, a_elo)
        prob = h_win_prob if outcome == h else (1.0 - h_win_prob)
        
        dec_odds = american_to_decimal(row['odds'])
        ev_val = calculate_ev(prob, dec_odds)
        
        results.append({
            'game': f"{row['away_team']} @ {row['home_team']}",
            'outcome': row['outcome'],
            'prob': prob,
            'odds': row['odds'],
            'ev': ev_val
        })
    
    df = pd.DataFrame(results)
    print(f"Total market lines: {len(df)}")
    print(f"Lines with EV >= 0.03: {len(df[df['ev'] >= 0.03])}")
    print("\n--- Top +EV Bets ---")
    print(df[df['ev'] >= 0.03].sort_values(by='ev', ascending=False).to_string())

if __name__ == "__main__":
    check()

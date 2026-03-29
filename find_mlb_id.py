import requests
import os
from dotenv import load_dotenv

load_dotenv()

def find_mlb_league_id():
    key = os.getenv("API_SPORTS_KEY")
    url = "https://v1.baseball.api-sports.io/leagues"
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": "v1.baseball.api-sports.io"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        leagues = response.json().get("response", [])
        for l in leagues:
            if "MLB" in l['name']:
                print(f"ID: {l['id']} | Name: {l['name']} | Country: {l['country']['name']}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    find_mlb_league_id()

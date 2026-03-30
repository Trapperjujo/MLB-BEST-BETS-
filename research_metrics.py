import requests

def research_categories():
    print("--- Researching MLB Stats API leadership categories ---")
    url = "https://statsapi.mlb.com/api/v1/stats/leaderCategories"
    try:
        r = requests.get(url)
        data = r.json()
        categories = sorted([c.get("displayName") for c in data])
        
        # Look for target metrics
        targets = ["weightedOnBaseAverage", "onBasePlusSlugging", "outsAboveAverage", "sweetSpotPercentage"]
        found = [c for c in categories if any(t.lower() in c.lower() for t in targets)]
        
        print(f"Total Categories: {len(categories)}")
        print(f"Target Sync: {found}")
        return found
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    research_categories()

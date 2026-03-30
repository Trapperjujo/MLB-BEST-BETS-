import sys
import os
from datetime import datetime

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.services.orchestrator import sync_mlb_data
from core.database import terminal_db

def test_full_system_sync():
    print("🚀 Initiating Triple-Source Architecture Audit...")
    
    # 1. Test Layer 1 (API) and Layer 2 (Scraper)
    print("📡 Synchronizing Daily Slate (Layer 1-2)...")
    try:
        # Using small bankroll for test
        df, live, standings, leaders = sync_mlb_data(1000, 0.25, 0.91)
        
        if not df.empty:
            print(f"✅ LAYER 1/2 SUCCESS: Ingested {len(df)} game betting opportunities.")
            print(f"💎 Primary Source used: {df.iloc[0].get('data_source', 'Unknown')}")
        else:
            print("⚠️ LAYER 1/2 WARNING: Feed empty (likely no games today).")

        # 2. Test Layer 3 (DuckDB Persistence)
        print("💾 Verifying Layer 3 (DuckDB) Glossary Cache...")
        count = terminal_db.conn.execute("SELECT count(*) FROM glossary_batting_2026").fetchone()[0]
        if count > 0:
            print(f"✅ LAYER 3 SUCCESS: DuckDB currently holds {count} team records in glossary_batting.")
        else:
            print("❌ LAYER 3 FAILURE: Glossary cache is empty.")

    except Exception as e:
        print(f"❌ ARCHITECTURE CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    test_full_system_sync()

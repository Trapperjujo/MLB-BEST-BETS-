import sys
import os

# Inject project root for institutional imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckdb
import pandas as pd
from core.database import DB_PATH

def run_audit():
    print(f"--- Initiating 2026 Institutional Data Audit ---")
    print(f"Local Store: {DB_PATH}")
    
    conn = duckdb.connect(DB_PATH)
    
    tables = ["glossary_batting_2026", "glossary_pitching_2026", "glossary_fielding_2026"]
    
    for table in tables:
        try:
            count = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            cols = [c[1] for c in conn.execute(f"PRAGMA table_info('{table}')").fetchall()]
            
            print(f"\n[OK] Table: {table}")
            print(f"   - Record Count: {count} teams synchronized.")
            print(f"   - Column Integrity: {len(cols)} metrics ingested.")
            
            if "batting" in table:
                statcast_check = any(c in cols for c in ["Barrel%", "xBA", "xwOBA"])
                print(f"   - Statcast Resolution: {'High-Fidelity' if statcast_check else 'Standard'}")
                
        except Exception as e:
            print(f"[ERROR] Table: {table} - DATA MISSING or {e}")

    conn.close()
    status = "Authoritative" if count >= 30 else "Hydrating"
    print(f"\nAudit Complete: System is {status}.")

if __name__ == "__main__":
    run_audit()

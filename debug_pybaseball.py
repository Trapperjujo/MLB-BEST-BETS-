import pybaseball as pb
import pandas as pd

try:
    # Test a known team from 2024
    print("Fetching NYY 2024 schedule...")
    df = pb.schedule_and_record(2024, "NYY")
    print(df.head())
    print("\nColumns:", df.columns.tolist())
except Exception as e:
    print(f"Error: {e}")

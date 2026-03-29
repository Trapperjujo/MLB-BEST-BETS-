import pybaseball as pb
import pandas as pd

# Test multiple abbreviations for Yankees
test_abbrs = ["NYY", "NYA", "NY"]

for abbr in test_abbrs:
    print(f"Testing {abbr}...")
    try:
        df = pb.schedule_and_record(2024, abbr)
        print(f"Success for {abbr}")
        print(df.head(2))
        break
    except Exception as e:
        print(f"Failed for {abbr}")

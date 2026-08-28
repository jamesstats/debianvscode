import pandas as pd

df = pd.read_csv("/home/jkdebian/Documents/Electionfiles/MA_06.csv") 

# 1. Remove ' - ' before a single number/letter at the end (e.g., 'Precinct - 1' -> 'Precinct 1')
df["WP_NAME2"] = df["WP_NAME2"].str.replace(r"\s*-\s*(\d+[A-Z]?)$", r" \1", regex=True)

# 2. Insert a dash between double numbers separated by a space (e.g., 'Precinct 1 1' -> 'Precinct 1-1')
df["WP_NAME2"] = df["WP_NAME2"].str.replace(r"(\b\d+[A-Z]?)\s+(\d+[A-Z]?\b)", r"\1-\2", regex=True)

# Save to CSV
df.to_csv("/home/jkdebian/Documents/Electionfiles/MA_06_cleaned.csv", index=False)  
import pandas as pd

df = pd.read_csv(
    "C:/Users/Alvaro/github-limpio/tactical-narrative-graph-analysis/data/raw/statsbomb_passes.csv"
)
print(f"Total real passing edges: {len(df)}")
print(f"Unique passers: {df['passer'].nunique()}")
print(f"Unique receivers: {df['receiver'].nunique()}")
print(f"Teams: {df['team'].unique()}")
print("\nTop 10 passers:")
print(df["passer"].value_counts().head(10))
print("\nTop 10 receivers:")
print(df["receiver"].value_counts().head(10))
print("\nSample data:")
print(df[["passer", "receiver", "pass_outcome", "pass_length"]].head(10))

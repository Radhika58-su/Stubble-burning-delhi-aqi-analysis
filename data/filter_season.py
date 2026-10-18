import pandas as pd

df = pd.read_csv("tidy_aqi_all_stations.csv", parse_dates=["datetime"])

print("Full dataset:", df.shape)
print("Date range:", df["datetime"].min(), "to", df["datetime"].max())

# Filter to October-November across 2021, 2022, 2023 (stubble-burning season)
mask = (
    df["datetime"].dt.month.isin([10, 11]) &
    df["datetime"].dt.year.isin([2021, 2022, 2023])
)
season_df = df[mask].copy()

print("\nStubble season (Oct-Nov, 2021-2023) subset:", season_df.shape)
print("\nRows per station:")
print(season_df["station"].value_counts())

print("\nRows per year:")
print(season_df["datetime"].dt.year.value_counts().sort_index())

# Quick sanity check: average AQI value per station per year
print("\nAverage reading per station per year:")
print(season_df.groupby([season_df["datetime"].dt.year, "station"])["value"].mean())

season_df.to_csv("aqi_stubble_season_2021_2023.csv", index=False)
print("\nSaved: aqi_stubble_season_2021_2023.csv")
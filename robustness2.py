import pandas as pd
from scipy.stats import pearsonr, spearmanr

daily = pd.read_csv("data/aqi_fire_daily.csv", parse_dates=["date"], index_col="date")
daily["year"] = daily.index.year

daily["fires_d"] = daily.groupby("year")["fires_filtered"].diff()
daily["aqi_d"] = daily.groupby("year")["delhi_mean"].diff()
# change in fires on day t-1 vs change in AQI on day t (lag 1, within each season)
daily["fires_d_lag1"] = daily.groupby("year")["fires_d"].shift(1)

pair = daily[["fires_d_lag1", "aqi_d", "year"]].dropna()


def report(label, p):
    r, pv = pearsonr(p["fires_d_lag1"], p["aqi_d"])
    rho, pv_s = spearmanr(p["fires_d_lag1"], p["aqi_d"])
    print(f"{label:<34} n={len(p):>3}  pearson r={r:5.2f} (p={pv:.4f})  "
          f"spearman rho={rho:5.2f} (p={pv_s:.4f})")


report("All years", pair)
for y, g in pair.groupby("year"):
    report(f"Year {y}", g)

# The zero-fire day (2 Nov 2023) distorts the pairs for 3 Nov and 4 Nov 2023
bad = [pd.Timestamp("2023-11-03"), pd.Timestamp("2023-11-04")]
report("All years, minus 3-4 Nov 2023", pair[~pair.index.isin(bad)])
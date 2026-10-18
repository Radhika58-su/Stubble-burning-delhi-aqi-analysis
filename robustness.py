import pandas as pd

daily = pd.read_csv("data/aqi_fire_daily.csv", parse_dates=["date"], index_col="date")
daily["year"] = daily.index.year
MAX_LAG = 4

# Mask for days within +/-2 days of Diwali
DIWALI = ["2021-11-04", "2022-10-24", "2023-11-12"]
near_diwali = pd.Series(False, index=daily.index)
for d in DIWALI:
    mask = abs(daily.index - pd.Timestamp(d)) <= pd.Timedelta(days=2)
    near_diwali = near_diwali | pd.Series(mask, index=daily.index)


def corr_by_lag(fires, aqi, keep=None):
    out = {}
    for lag in range(MAX_LAG + 1):
        shifted = fires.groupby(daily["year"]).shift(lag)  # never crosses seasons
        pair = pd.DataFrame({"f": shifted, "a": aqi}).dropna()
        if keep is not None:
            pair = pair[keep.reindex(pair.index)]
        out[lag] = round(pair["f"].corr(pair["a"]), 2)
    return pd.Series(out)


fires_d = daily.groupby("year")["fires_filtered"].diff()
aqi_d = daily.groupby("year")["delhi_mean"].diff()

results = pd.DataFrame({
    "levels": corr_by_lag(daily["fires_filtered"], daily["delhi_mean"]),
    "levels, no Diwali": corr_by_lag(daily["fires_filtered"], daily["delhi_mean"], keep=~near_diwali),
    "daily change": corr_by_lag(fires_d, aqi_d),
})
results.index.name = "lag_days"
print(results)

zero = daily[daily["fires_filtered"] == 0]
print("\nDays with zero filtered fire detections:", len(zero))
print(zero.index.strftime("%Y-%m-%d").tolist())
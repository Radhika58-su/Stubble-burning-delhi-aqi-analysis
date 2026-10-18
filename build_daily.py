import pandas as pd

# ---------- FIRMS: convert UTC timestamps to IST dates ----------
fires = pd.read_csv("data/firms_raw_2021_2023.csv", parse_dates=["acq_date"])
print("Confidence values:\n", fires["confidence"].value_counts())
print("\nType values:\n", fires["type"].value_counts())

hhmm = fires["acq_time"].astype(str).str.zfill(4)
utc_ts = pd.to_datetime(
    fires["acq_date"].dt.strftime("%Y-%m-%d") + " " + hhmm.str[:2] + ":" + hhmm.str[2:],
    utc=True,
)
fires["local_date"] = utc_ts.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None).dt.normalize()

# Filtered version: drop low-confidence detections, keep presumed vegetation fires
keep = fires["confidence"].isin(["n", "h"]) & (fires["type"] == 0)
print(f"\nFilter keeps {keep.sum()} of {len(fires)} detections")

# ---------- AQI: daily average per station ----------
aqi = pd.read_csv("data/aqi_stubble_season_2021_2023.csv", parse_dates=["datetime"])
print(f"\nShare of AQI readings at the 500 cap: {(aqi['value'] >= 500).mean():.1%}")
aqi["date"] = aqi["datetime"].dt.normalize()
daily = aqi.pivot_table(index="date", columns="station", values="value", aggfunc="mean")
daily["delhi_mean"] = daily.mean(axis=1)

# ---------- Join on date ----------
all_counts = fires.groupby("local_date").size()
filtered_counts = fires[keep].groupby("local_date").size()
daily["fires_all"] = all_counts.reindex(daily.index).fillna(0).astype(int)
daily["fires_filtered"] = filtered_counts.reindex(daily.index).fillna(0).astype(int)

print("\nDaily table shape:", daily.shape)
print("Days with no AQI at all:", daily["delhi_mean"].isna().sum())
print(daily.head())
daily.to_csv("data/aqi_fire_daily.csv")
print("\nSaved data/aqi_fire_daily.csv")
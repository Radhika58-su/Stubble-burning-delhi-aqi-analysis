import pandas as pd
import matplotlib.pyplot as plt

daily = pd.read_csv("data/aqi_fire_daily.csv", parse_dates=["date"], index_col="date")
daily["year"] = daily.index.year

MAX_LAG = 7

# Correlation between fires on day (t - lag) and Delhi AQI on day t.
# The shift is done inside each year, so a lag never crosses from one season into the next.
rows = []
for lag in range(MAX_LAG + 1):
    shifted = daily.groupby("year")["fires_filtered"].shift(lag)
    pair = pd.DataFrame(
        {"fires": shifted, "aqi": daily["delhi_mean"], "year": daily["year"]}
    ).dropna()
    row = {"lag_days": lag}
    for year, g in pair.groupby("year"):
        row[str(year)] = g["fires"].corr(g["aqi"])
    row["pooled"] = pair["fires"].corr(pair["aqi"])
    row["pooled_spearman"] = pair["fires"].corr(pair["aqi"], method="spearman")
    rows.append(row)

result = pd.DataFrame(rows).set_index("lag_days").round(2)
print(result)
print("\nBest lag (highest correlation) per column:")
print(result.idxmax())
result.to_csv("data/lag_correlation.csv")

# Chart 1: correlation vs lag
ax = result[["2021", "2022", "2023", "pooled"]].plot(marker="o", figsize=(8, 5))
ax.set_xlabel("Lag (days after the fires)")
ax.set_ylabel("Correlation with Delhi mean AQI")
ax.set_title("Fire count vs Delhi AQI, by lag")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("data/lag_correlation.png", dpi=150)
plt.close()

# Chart 2: each season, AQI line over fire-count bars
fig, axes = plt.subplots(3, 1, figsize=(10, 9))
for ax, (year, g) in zip(axes, daily.groupby("year")):
    ax2 = ax.twinx()
    ax2.bar(g.index, g["fires_filtered"], color="tab:orange", alpha=0.4)
    ax2.set_ylabel("Fire detections")
    ax.set_zorder(ax2.get_zorder() + 1)  # draw the AQI line on top of the bars
    ax.patch.set_visible(False)
    ax.plot(g.index, g["delhi_mean"], color="tab:red")
    ax.set_ylabel("Delhi mean AQI")
    ax.set_title(str(year))
plt.tight_layout()
plt.savefig("data/season_overview.png", dpi=150)
plt.close()

print("\nSaved data/lag_correlation.csv, lag_correlation.png, season_overview.png")
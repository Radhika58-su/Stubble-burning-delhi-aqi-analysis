# Stubble Burning vs Delhi Air Quality: 3-Season Analysis

Does a rise in crop-residue fires in the Punjab-Haryana region show up in Delhi's air quality
the next day? This project joins NASA satellite fire detections with hourly AQI readings from
three Delhi monitoring stations for the October-November season of 2021, 2022 and 2023.

## Data

- **Fires:** NASA FIRMS, VIIRS S-NPP (Standard Processing, `VIIRS_SNPP_SP`), pulled through the
  FIRMS area API for the box 73.8,27.6,77.6,32.6 (west,south,east,north), 1 Oct to 30 Nov each year.
  190,641 detections.
- **Air quality:** hourly AQI for Anand Vihar, ITO and Punjabi Bagh (CPCB/DPCC data, from the
  OpenCity "Delhi Hourly Air Quality Reports" dataset). 153,277 hourly readings for 2017-2023,
  of which 12,319 fall in the Oct-Nov window used here.

## Method

1. The CPCB export is a nested grid (one small table per month, rows = days, columns = hours),
   so a custom parser turns it into a tidy table of station, timestamp and value.
2. FIRMS timestamps are UTC and AQI timestamps are IST. Fire times are converted to IST before
   counting fires per day, otherwise the night-time satellite pass lands on the wrong date.
3. Fire counts keep detections with nominal or high confidence and type 0 (presumed vegetation
   fire): 181,835 of 190,641.
4. Daily Delhi AQI is the mean of the three stations' hourly readings.
5. Fires on day t-lag are correlated with AQI on day t, with lags never crossing from one
   season into the next.
6. Because fires and AQI both rise through the season, the analysis is repeated on day-to-day
   changes (today minus yesterday) to remove the seasonal trend.

## Results

Correlation between daily fire count and Delhi mean AQI (all three seasons pooled):

| Lag (days) | Levels | Levels, Diwali +/-2 days removed | Day-to-day change |
|---|---|---|---|
| 0 | 0.47 | 0.46 | 0.05 |
| 1 | 0.50 | 0.49 | 0.29 |
| 2 | 0.45 | 0.45 | -0.09 |
| 3 | 0.43 | 0.44 | -0.01 |
| 4 | 0.41 | 0.41 | -0.03 |

- Fires and AQI move together through the season (r about 0.5), and removing Diwali week
  does not change that.
- After removing the seasonal trend, the only lag with a clear signal is 1 day:
  r = 0.29 (n = 177, p = 0.0001), and r = 0.30 without 3-4 Nov 2023.
- The sign is positive in each season on its own: r = 0.32 (2021), 0.32 (2022), 0.24 (2023).
  Single seasons have only 59 days each, and 2023 alone is not significant at the 5% level (p = 0.062).

Charts: `data/lag_correlation.png` and `data/season_overview.png`.

## Limitations

- **This is association, not causation.** r = 0.3 means about 9% of day-to-day AQI change is
  linked to fire change. No weather data (wind, rain, cloud) is included.
- The fire box is a rough rectangle. It covers Punjab and Haryana but also parts of neighbouring
  states, Pakistan and Delhi itself.
- A day with zero detections can mean cloud or smoke blocking the satellite, not no fires.
- AQI is capped at 500 (6.2% of season readings), which flattens the worst days.
- Only three Delhi stations, and only VIIRS S-NPP. Gurugram and other NCR stations are not included.
- The lag was picked after looking at lags 0-4, and consecutive days are not independent,
  so the p-values are optimistic.

## How to run

Setup:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

Create a `.env` file in the project root with your free NASA FIRMS key
(https://firms.modaps.eosdis.nasa.gov/api/map_key/), one line, no quotes:

    FIRMS_MAP_KEY=your_key_here

AQI scripts run from inside the `data` folder:

    cd data
    python download-aqi.py
    python parse_aqi.py
    python filter_season.py
    cd ..

Fire and analysis scripts run from the project root:

    python download_firms.py
    python build_daily.py
    python lag_analysis.py
    python robustness.py
    python robustness2.py

`download_firms.py` retries failed requests and can be re-run safely; it skips chunks it already has.
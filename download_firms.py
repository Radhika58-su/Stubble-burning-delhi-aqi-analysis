import io
import os
import time
from datetime import date, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("FIRMS_MAP_KEY")
if not key:
    raise SystemExit("FIRMS_MAP_KEY not found. Check your .env file.")

SOURCE = "VIIRS_SNPP_SP"
BBOX = "73.8,27.6,77.6,32.6"  # west,south,east,north (rough Punjab + Haryana box)
YEARS = [2021, 2022, 2023]
CHUNK_DIR = "data/firms_chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)


def fetch_chunk(start_day, days, retries=4):
    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{key}/{SOURCE}/{BBOX}/{days}/{start_day.isoformat()}"
    )
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200 and response.text.startswith("latitude"):
                return response.text
            print(f"  {start_day}: unexpected response (status {response.status_code}): {response.text[:150]}")
        except requests.RequestException as e:
            # print only the error type: the full message would contain the URL (and your key)
            print(f"  {start_day}: attempt {attempt} failed ({type(e).__name__})")
        time.sleep(5 * attempt)
    return None


failed = []
for year in YEARS:
    current = date(year, 10, 1)
    end = date(year, 11, 30)
    while current <= end:
        days = min(5, (end - current).days + 1)
        path = f"{CHUNK_DIR}/{current.isoformat()}.csv"
        if os.path.exists(path):
            print(f"{current}: already downloaded, skipping")
        else:
            text = fetch_chunk(current, days)
            if text is None:
                failed.append(current)
            else:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(text)
                rows = len(text.strip().splitlines()) - 1
                print(f"{current} (+{days} days): {rows} fire detections")
                time.sleep(1)
        current += timedelta(days=days)

if failed:
    print("\nThese chunks failed. Run the script again to retry only them:")
    for d in failed:
        print(" ", d)
    raise SystemExit("Combined file not built until all chunks are downloaded.")

files = sorted(os.listdir(CHUNK_DIR))
fires = pd.concat(
    [pd.read_csv(f"{CHUNK_DIR}/{name}") for name in files], ignore_index=True
)
fires.to_csv("data/firms_raw_2021_2023.csv", index=False)

fires["acq_date"] = pd.to_datetime(fires["acq_date"])
print("\nChunks:", len(files), "(expected 39)")
print("Total detections:", len(fires))
print("Date range:", fires["acq_date"].min().date(), "to", fires["acq_date"].max().date())
print(fires.groupby(fires["acq_date"].dt.year).size())
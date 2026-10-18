import csv
import re
import pandas as pd

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

HEADER_PATTERN = re.compile(r"^([A-Za-z]+)-(\d{4})$")


def parse_station_file(path, station_name):
    """
    Parses CPCB's nested month-grid CSV format into a tidy list of
    (station, datetime, value) records.
    """
    records = []
    current_year = None
    current_month = None
    current_hours = None

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].strip() == "" or row[0].strip() == '"':
                continue  # skip blank / stray quote lines

            first = row[0].strip()

            # Skip the stray top-of-file "Year,2017" line
            if first.lower() == "year":
                continue

            # Detect a new month header, e.g. "January-2017"
            match = HEADER_PATTERN.match(first)
            if match:
                month_name, year = match.groups()
                month_name = month_name.lower()
                if month_name not in MONTHS:
                    current_month = None
                    continue
                current_month = MONTHS[month_name]
                current_year = int(year)
                current_hours = row[1:]  # e.g. ['00:00:00', '01:00:00', ...]
                continue

            # Otherwise, this should be a day-of-month data row: "1,388.0,396.0,..."
            if current_month is None or not first.isdigit():
                continue  # not a data row we recognize, skip safely

            day = int(first)
            values = row[1:]

            for hour_str, val in zip(current_hours, values):
                val = val.strip()
                if val == "" or val.lower() == "nan":
                    continue
                try:
                    value = float(val)
                except ValueError:
                    continue
                try:
                    hour = int(hour_str.split(":")[0])
                    timestamp = pd.Timestamp(
                        year=current_year, month=current_month, day=day, hour=hour
                    )
                except (ValueError, IndexError):
                    continue  # skip invalid dates (e.g. Feb 30)

                records.append({
                    "station": station_name,
                    "datetime": timestamp,
                    "value": value
                })

    return pd.DataFrame(records)


if __name__ == "__main__":
    files = {
        "Anand Vihar": "anand_vihar.csv",
        "ITO": "ito.csv",
        "Punjabi Bagh": "punjabi_bagh.csv",
    }

    all_data = []
    for station, path in files.items():
        print(f"Parsing {station} ({path})...")
        df = parse_station_file(path, station)
        print(f"  -> {len(df)} valid hourly readings parsed")
        df.to_csv(f"tidy_{path}", index=False)
        all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)
    combined.to_csv("tidy_aqi_all_stations.csv", index=False)
    print(f"\nCombined dataset: {len(combined)} rows -> tidy_aqi_all_stations.csv")
    print("\nDate range:", combined["datetime"].min(), "to", combined["datetime"].max())
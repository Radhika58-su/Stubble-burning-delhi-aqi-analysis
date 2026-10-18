import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("FIRMS_MAP_KEY")
if not key:
    raise SystemExit("FIRMS_MAP_KEY not found. Check your .env file.")

url = f"https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/{key}/VIIRS_SNPP_SP"
response = requests.get(url, timeout=30)
print("Status code:", response.status_code)
print(response.text)
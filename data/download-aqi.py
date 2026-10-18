import requests

stations = {
    "anand_vihar.csv": "https://data.opencity.in/dataset/0dc7b9fe-9fd4-46ee-a37e-88f0bd6f6362/resource/c1d1fe4e-d515-4b2c-b7f3-b876b00f6c58/download/6c3a6f63-8294-44c0-88dd-ad078ef4c91b.csv",
    "ito.csv": "https://data.opencity.in/dataset/0dc7b9fe-9fd4-46ee-a37e-88f0bd6f6362/resource/8e319d28-e9e0-49d7-b735-7f6829b1baf3/download/f2ea6fc8-ee3e-44ff-988c-0695b73e5639.csv",
    "punjabi_bagh.csv": "https://data.opencity.in/dataset/0dc7b9fe-9fd4-46ee-a37e-88f0bd6f6362/resource/da0ab893-d803-4640-aa12-6141ed22d492/download/ae701f4b-81d0-430d-bb9d-595d58e87f2d.csv",
}

headers = {"User-Agent": "Mozilla/5.0"}

for filename, url in stations.items():
    print(f"Downloading {filename}...")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Saved {filename} ({len(response.content)} bytes)")

print("\nAll downloads complete!")
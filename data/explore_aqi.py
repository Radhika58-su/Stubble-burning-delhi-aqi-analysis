import pandas as pd
files = ["anand_vihar.csv", "ito.csv", "Punjabi_bagh.csv"]

for f in files:
    print(f"\n{'='*50}")
    print(f"File:{f}")
    df = pd.read_csv(f)
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print(df.head(5))


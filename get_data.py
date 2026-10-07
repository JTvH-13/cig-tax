"""Download the CDC Tax Burden on Tobacco data and build data/clean.csv."""

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

URL = "https://data.cdc.gov/resource/7nwe-3aj9.csv?$limit=50000"
RAW = Path("data/raw/tax_burden_on_tobacco.csv")
CLEAN = Path("data/clean.csv")

MEASURES = {
    "Average Cost per pack": "price",
    "Cigarette Consumption (Pack Sales Per Capita)": "packs_pc",
    "State Tax per pack": "state_tax",
    "Gross Cigarette Tax Revenue": "revenue",
}

# Download and save the file exactly as the portal sends it
with urlopen(URL) as response:
    raw_bytes = response.read()
RAW.parent.mkdir(parents=True, exist_ok=True)
RAW.write_bytes(raw_bytes)

raw = pd.read_csv(BytesIO(raw_bytes))
print(f"Raw rows: {len(raw):,}")
assert len(raw) == 15_300, f"expected 15,300 raw rows, got {len(raw):,}"

# Keep the four measures, one row per state and year
df = raw[raw["submeasuredesc"].isin(MEASURES)]
clean = (
    df.pivot(index=["locationdesc", "year"], columns="submeasuredesc", values="data_value")
    .rename(columns=MEASURES)
    .reset_index()
    .rename(columns={"locationdesc": "state"})
)
clean = clean[["state", "year", "price", "packs_pc", "state_tax", "revenue"]]
clean = clean.sort_values(["state", "year"]).reset_index(drop=True)
clean.columns.name = None

CLEAN.parent.mkdir(parents=True, exist_ok=True)
clean.to_csv(CLEAN, index=False)
print(f"Clean rows: {len(clean):,} ({clean['state'].nunique()} states, "
      f"{clean['year'].min()}-{clean['year'].max()})")

ca = clean[(clean["state"] == "California") & clean["year"].between(2014, 2019)]
print("\nCalifornia, 2014-2019:")
print(ca.to_string(index=False))

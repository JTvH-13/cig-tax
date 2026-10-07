"""Download the CDC Tax Burden on Tobacco data, save it raw, and pivot it into data/clean.csv."""
from pathlib import Path
import pandas as pd

URL = "https://data.cdc.gov/resource/7nwe-3aj9.csv?$limit=50000"
RAW = Path("data/raw/tax_burden.csv")
CLEAN = Path("data/clean.csv")

# submeasuredesc in the raw data -> column name in clean.csv
MEASURES = {
    "Average Cost per pack": "price",
    "Cigarette Consumption (Pack Sales Per Capita)": "packs_pc",
    "State Tax per pack": "state_tax",
    "Gross Cigarette Tax Revenue": "revenue",
}

# 1. Download and save unmodified
RAW.parent.mkdir(parents=True, exist_ok=True)
raw = pd.read_csv(URL)
raw.to_csv(RAW, index=False)
print(f"raw rows: {len(raw)}")
assert len(raw) == 15300, "expected 15,300 raw rows"

# 2. Pivot to one row per state and year
long = raw[raw["submeasuredesc"].isin(MEASURES)].rename(columns={"locationdesc": "state"})
clean = (
    long.pivot(index=["state", "year"], columns="submeasuredesc", values="data_value")
    .rename(columns=MEASURES)
    .reset_index()[["state", "year", "price", "packs_pc", "state_tax", "revenue"]]
    .sort_values(["state", "year"])
)
clean.columns.name = None
clean.to_csv(CLEAN, index=False)
print(f"clean rows: {len(clean)}")

# 3. California, 2014-2019
print(clean[(clean["state"] == "California") & clean["year"].between(2014, 2019)].to_string(index=False))

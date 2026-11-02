
import pandas as pd

# Read original UNODC dataset
df = pd.read_excel(
    "data/raw/total_count_intentional_homicide.xlsx",
    header=2
)

# Filter relevant homicide observations
df = df[
    (df["Indicator"] == "Victims of intentional homicide")
    & (df["Sex"] == "Total")
    & (df["Dimension"] == "Total")
    & (df["Age"] == "Total")
    & (df["Category"] == "Total")
].copy()

# Identify the two measurements
df["Unit of measurement"] = (
    df["Unit of measurement"].astype(str).str.strip()
)

df["Measure"] = df["Unit of measurement"].apply(
    lambda x: (
        "Count" if "count" in x.lower()
        else "Rate" if "rate" in x.lower()
        else None
    )
)

# Keep only counts and rates
df = df[df["Measure"].notna()].copy()

# Columns identifying each country-year observation
index_columns = ["Iso3_code", "Country", "Year"]

# Remove unnecessary columns
df = df[
    index_columns + ["VALUE", "Measure"]
]

# Check for duplicate country-year-measure combinations
duplicates = df.duplicated(
    subset=index_columns + ["Measure"],
    keep=False
)

if duplicates.any():
    raise ValueError(
        "Duplicate country-year-measure observations found. "
        "Check the source data before pivoting."
    )

# Convert from long format to wide format
wide_df = df.pivot(
    index=index_columns,
    columns="Measure",
    values="VALUE"
).reset_index()

# Ensure both columns exist
wide_df.columns.name = None

for col in ["Count", "Rate"]:
    if col not in wide_df.columns:
        wide_df[col] = pd.NA

# Arrange columns
wide_df = wide_df[
    ["Iso3_code", "Country", "Year", "Count", "Rate"]
]

# Filter to the dashboard study period (2015–2024)
wide_df = wide_df[
    (wide_df["Year"] >= 2015) &
    (wide_df["Year"] <= 2024)
].copy()

# Sort data
wide_df = wide_df.sort_values(
    ["Country", "Year"]
)


# Export processed dataset
wide_df.to_csv(
    "data/processed/HomicideCountsAndRates.csv",
    index=False
)

print("Data wrangling completed!")
print(wide_df.head(10))
print("\nDataset shape:", wide_df.shape)
print("\nMissing values:")
print(wide_df.isna().sum())

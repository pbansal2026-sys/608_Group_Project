
import pandas as pd

# ==========================================
# 1. LOAD AND PREPARE THE DATA
# ==========================================

df = pd.read_csv("data/processed/HomicideCountsAndRates.csv")

countries = df[["Iso3_code", "Country"]].drop_duplicates()
years = pd.DataFrame({"Year": range(2015, 2025)})

# Create a complete country-year panel
panel = (
    countries.merge(years, how="cross")
    .merge(df, on=["Iso3_code", "Country", "Year"], how="left")
    .sort_values(["Iso3_code", "Year"])
    .reset_index(drop=True)
)

# Preserve original rates and create imputation flag
panel["Rate_Original"] = panel["Rate"]
panel["Was_Imputed"] = False


# ==========================================
# 2. INTERPOLATE ELIGIBLE MISSING RATES
# ==========================================

def impute_country(group):
    group = group.sort_values("Year").copy()

    rates = group["Rate"].to_numpy(copy=True)
    years = group["Year"].to_numpy()

    i = 0

    while i < len(rates):
        if pd.notna(rates[i]):
            i += 1
            continue

        start = i

        while i < len(rates) and pd.isna(rates[i]):
            i += 1

        end = i
        gap_length = end - start

        # Only interpolate gaps of 1–5 years
        # that have observed values on both sides
        if gap_length <= 5 and start > 0 and end < len(rates):

            left_rate = rates[start - 1]
            right_rate = rates[end]

            left_year = years[start - 1]
            right_year = years[end]

            for j in range(start, end):
                rates[j] = (
                    left_rate
                    + (right_rate - left_rate)
                    * (years[j] - left_year)
                    / (right_year - left_year)
                )

                group.loc[group.index[j], "Was_Imputed"] = True

    group["Rate"] = rates
    return group


result = pd.concat(
    [
        impute_country(group)
        for _, group in panel.groupby("Iso3_code", sort=False)
    ],
    ignore_index=True
)


# ==========================================
# 3. SAVE THE IMPUTED DATASET
# ==========================================

output_path = "data/processed/HomicideRates_2015_2024_Imputed.csv"

result.to_csv(output_path, index=False)


# ==========================================
# 4. VALIDATE THE IMPUTED DATASET
# ==========================================

print("\n========== DATASET SUMMARY ==========")

print("Total rows:", len(result))
print("Unique entities:", result["Iso3_code"].nunique())
print("Rates imputed:", result["Was_Imputed"].sum())
print("Rates still missing:", result["Rate"].isna().sum())


# Check original observed rates were unchanged
observed = result["Rate_Original"].notna()

changed = (
    observed
    & ((result["Rate"] - result["Rate_Original"]).abs() > 1e-9)
)

# Check imputation flags
incorrect_flags = (
    result["Was_Imputed"]
    & result["Rate_Original"].notna()
)

unflagged_fills = (
    result["Rate_Original"].isna()
    & result["Rate"].notna()
    & ~result["Was_Imputed"]
)

# Check zero rates
zero_rates = (
    (result["Rate_Original"] == 0)
    & (result["Rate"] == 0)
)

# Verify gap length and boundaries
gap_errors = []

for code, group in result.groupby("Iso3_code"):
    group = group.sort_values("Year").reset_index(drop=True)

    flags = group["Was_Imputed"].to_numpy()
    original = group["Rate_Original"].to_numpy()
    years = group["Year"].to_numpy()

    i = 0

    while i < len(group):
        if not flags[i]:
            i += 1
            continue

        start = i

        while i < len(group) and flags[i]:
            i += 1

        end = i

        if (
            end - start > 5
            or start == 0
            or end == len(group)
            or pd.isna(original[start - 1])
            or pd.isna(original[end])
        ):
            gap_errors.append(code)


# Check interpolated values are between observed anchors
interpolation_errors = []

for code, group in result.groupby("Iso3_code"):
    group = group.sort_values("Year").reset_index(drop=True)

    flags = group["Was_Imputed"].to_numpy()
    rates = group["Rate"].to_numpy()
    original = group["Rate_Original"].to_numpy()

    i = 0

    while i < len(group):
        if not flags[i]:
            i += 1
            continue

        start = i

        while i < len(group) and flags[i]:
            i += 1

        end = i

        lower = min(original[start - 1], original[end])
        upper = max(original[start - 1], original[end])

        for j in range(start, end):
            if not (lower - 1e-9 <= rates[j] <= upper + 1e-9):
                interpolation_errors.append(code)


# ==========================================
# 5. PRINT VALIDATION RESULTS
# ==========================================

checks = {
    "Expected 1,680 rows": len(result) == 1680,
    "Expected 168 entities": result["Iso3_code"].nunique() == 168,
    "Exactly 49 rates imputed": result["Was_Imputed"].sum() == 49,
    "374 rates remain missing": result["Rate"].isna().sum() == 374,
    "Original rates unchanged": changed.sum() == 0,
    "Imputation flags correct": incorrect_flags.sum() == 0,
    "No unflagged filled values": unflagged_fills.sum() == 0,
    "21 zero rates preserved": zero_rates.sum() == 21,
    "Five-year and boundary rules followed": len(gap_errors) == 0,
    "Interpolated values within anchor range": len(interpolation_errors) == 0,
}

print("\n========== VALIDATION RESULTS ==========")

for check, passed in checks.items():
    print(f"{check}: {'PASS' if passed else 'FAIL'}")

print("\n========================================")

if all(checks.values()):
    print("FINAL RESULT: ALL CHECKS PASSED")
else:
    print("FINAL RESULT: CHECK REQUIRED")

print("Saved dataset:", output_path)

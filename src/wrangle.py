import pandas as pd
from pathlib import Path

# ============================================================
# SETTINGS
# ============================================================

RAW_PATH = Path("data/raw/total_count_intentional_homicide.xlsx")
OUT_DIR = Path("data/processed")

START_YEAR, END_YEAR = 2015, 2024
YEARS = list(range(START_YEAR, END_YEAR + 1))

# Interpolate only internal gaps of 1 or 2 consecutive years.
MAX_GAP = 2

DIMENSIONS = {
    "by mechanisms": "mechanism",
    "by relationship to perpetrator": "relationship",
    "by situational context": "context",
    "by citizenship": "citizenship",
}

# These subcategories overlap with their parent categories.
# Collapse them to the parent category to avoid double counting.
SUB_TO_PARENT = {
    "Firearms or explosives - firearms": "Firearms or explosives",
    "Another weapon - sharp object": "Another weapon",
    "Intimate partner or family member: Family member":
        "Intimate partner or family member",
    "Intimate partner or family member: Intimate partner":
        "Intimate partner or family member",
    "Socio-political homicide - terrorist offences":
        "Socio-political homicide",
}

ID = [
    "Iso3_code",
    "Country",
    "Region",
    "Subregion",
    "Year",
    "Sex",
]

ID_NO_YEAR = [col for col in ID if col != "Year"]

OUTPUT_COLS = ID + [
    "Category",
    "Count",
    "Rate",
    "Share_pct",
    "Was_Imputed_Count",
    "Was_Imputed_Rate",
    "Was_Imputed",
    "Rate_Derived",
    "From_Subcategory",
    "Sum_vs_Total",
]


# ============================================================
# 1. LOAD AND RESHAPE RAW DATA
# ============================================================

def load_raw():
    """Load source data and reshape Counts and Rates into separate columns."""

    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"Could not find source file: {RAW_PATH}"
        )

    df = pd.read_excel(RAW_PATH, header=2)

    required = [
        "Indicator",
        "Dimension",
        "Category",
        "Sex",
        "Age",
        "Unit of measurement",
        "Year",
        "VALUE",
        "Iso3_code",
        "Country",
        "Region",
        "Subregion",
    ]

    missing_cols = sorted(set(required) - set(df.columns))

    if missing_cols:
        raise ValueError(
            f"Missing required source columns: {missing_cols}"
        )

    text_cols = [
        "Indicator",
        "Dimension",
        "Category",
        "Sex",
        "Age",
        "Unit of measurement",
        "Iso3_code",
        "Country",
        "Region",
        "Subregion",
    ]

    for col in text_cols:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

    df["Year"] = pd.to_numeric(
        df["Year"],
        errors="coerce",
    )

    df["VALUE"] = pd.to_numeric(
        df["VALUE"],
        errors="coerce",
    )

    # Keep intentional homicide victims, total age, and study years.
    df = df[
        (df["Indicator"] == "Victims of intentional homicide")
        & (df["Age"] == "Total")
        & df["Year"].between(START_YEAR, END_YEAR)
        & df["Unit of measurement"].isin(
            [
                "Counts",
                "Rate per 100,000 population",
            ]
        )
    ].copy()

    df["Measure"] = df["Unit of measurement"].map(
        {
            "Counts": "Count",
            "Rate per 100,000 population": "Rate",
        }
    )

    # Each source key should have no more than one Count and one Rate.
    keys = ID + [
        "Dimension",
        "Category",
        "Measure",
    ]

    duplicates = df.duplicated(
        subset=keys,
        keep=False,
    )

    if duplicates.any():
        examples = df.loc[
            duplicates,
            keys,
        ].head(10)

        raise ValueError(
            "Duplicate observations found for source keys.\n"
            f"{examples.to_string(index=False)}"
        )

    wide = (
        df.pivot(
            index=ID + ["Dimension", "Category"],
            columns="Measure",
            values="VALUE",
        )
        .reset_index()
    )

    wide.columns.name = None

    for col in ["Count", "Rate"]:
        if col not in wide.columns:
            wide[col] = pd.NA

    return wide


# ============================================================
# 2. SHORT-GAP INTERPOLATION
# ============================================================

def fill_short_gaps(series):
    """
    Fill internal missing runs up to MAX_GAP years.

    - Does not fill leading or trailing missing values.
    - Does not replace observed zero values.
    - Does not fill gaps longer than MAX_GAP.
    """

    values = pd.to_numeric(
        series.reset_index(drop=True),
        errors="coerce",
    )

    missing = values.isna()

    # Identify consecutive runs of missing/non-missing values.
    run_id = (missing != missing.shift()).cumsum()

    # Length of each run, repeated across its rows.
    run_length = missing.groupby(run_id).transform("sum")

    # Interpolate only between observed values.
    interpolated = values.interpolate(
        method="linear",
        limit_area="inside",
    )

    use = (
        missing
        & (run_length <= MAX_GAP)
        & interpolated.notna()
    )

    result = values.where(
        ~use,
        interpolated,
    )

    return pd.Series(
        result.to_numpy(),
        index=series.index,
    )


def interpolate_panel(data, group_cols, value_cols):
    """
    Expand each panel to all study years and interpolate eligible gaps.

    Separate flags are created for each value column:
      Was_Imputed_Count
      Was_Imputed_Rate

    Was_Imputed is True if either measure was imputed.
    """

    if data.empty:
        return data.copy()

    keys = group_cols + ["Year"]

    if data.duplicated(keys).any():
        raise ValueError(
            f"Duplicate rows before interpolation for keys: {keys}"
        )

    groups = data[group_cols].drop_duplicates()

    year_frame = pd.DataFrame({
        "Year": YEARS,
    })

    panel = (
        groups.merge(
            year_frame,
            how="cross",
        )
        .merge(
            data,
            on=keys,
            how="left",
        )
        .sort_values(
            group_cols + ["Year"]
        )
        .reset_index(drop=True)
    )

    for col in value_cols:
        flag_col = f"Was_Imputed_{col}"

        original = pd.to_numeric(
            panel[col],
            errors="coerce",
        )

        filled = original.groupby(
            [panel[c] for c in group_cols],
            dropna=False,
        ).transform(fill_short_gaps)

        panel[col] = filled

        panel[flag_col] = (
            original.isna()
            & filled.notna()
        )

    panel["Was_Imputed"] = (
        panel.get("Was_Imputed_Count", False)
        | panel.get("Was_Imputed_Rate", False)
    )

    # Keep rows where at least one requested measure exists.
    return (
        panel.dropna(
            subset=value_cols,
            how="all",
        )
        .reset_index(drop=True)
    )


# ============================================================
# 3. OVERALL TOTALS, RATES, AND POPULATION ESTIMATES
# ============================================================

def overall_totals(wide):
    """
    Get overall homicide totals by country, year, and sex.

    Population is estimated from Count / Rate where Rate > 0.
    """

    totals = wide[
        (wide["Dimension"] == "Total")
        & (wide["Category"] == "Total")
    ].copy()

    totals = interpolate_panel(
        totals[ID + ["Count", "Rate"]],
        ID_NO_YEAR,
        ["Count", "Rate"],
    )

    totals["Population"] = (
        totals["Count"]
        / totals["Rate"]
        * 100_000
    ).where(
        totals["Rate"] > 0
    )

    return totals


def build_rates(totals):
    """Build the overall Total-sex rate dataset for the map and app."""

    result = totals[
        totals["Sex"] == "Total"
    ].copy()

    return result[
        [
            "Iso3_code",
            "Country",
            "Region",
            "Subregion",
            "Year",
            "Count",
            "Rate",
            "Was_Imputed_Count",
            "Was_Imputed_Rate",
            "Was_Imputed",
        ]
    ]


# ============================================================
# 4. DIMENSION CATEGORY PREPARATION
# ============================================================

def collapse_subcategories(data):
    """
    Use parent categories when available.

    If a parent category is absent, use its subcategories only when
    all expected subcategory components are present.
    """

    data = data.copy()

    data["From_Subcategory"] = False

    is_subcategory = data["Category"].isin(
        SUB_TO_PARENT
    )

    parents = data[
        ~is_subcategory
    ].copy()

    subs = data[
        is_subcategory
    ].copy()

    if subs.empty:
        return parents

    subs["Category"] = subs["Category"].map(
        SUB_TO_PARENT
    )

    subs["From_Subcategory"] = True

    # Require every expected subcategory component.
    subs = (
        subs.groupby(
            ID + ["Category"],
            dropna=False,
        )
        .agg(
            Count=(
                "Count",
                lambda values: values.sum(
                    min_count=len(values)
                ),
            ),
            Rate=(
                "Rate",
                lambda values: values.sum(
                    min_count=len(values)
                ),
            ),
            n=("Count", "size"),
            From_Subcategory=(
                "From_Subcategory",
                "first",
            ),
        )
        .reset_index()
    )

    expected_counts = (
        pd.Series(
            SUB_TO_PARENT.values()
        )
        .value_counts()
    )

    subs = subs[
        subs["n"]
        == subs["Category"].map(expected_counts)
    ].drop(
        columns="n"
    )

    # Parent observations take precedence over derived subcategories.
    combined = pd.concat(
        [parents, subs],
        ignore_index=True,
    )

    combined = (
        combined.sort_values(
            "From_Subcategory"
        )
        .drop_duplicates(
            subset=ID + ["Category"],
            keep="first",
        )
    )

    return combined


def build_citizenship_total(data):
    """
    Derive Total-sex citizenship counts only where both Male and Female
    values are available for the same country-year-category.

    Citizenship-specific rates are not derived here.
    """

    index_cols = [
        col for col in ID_NO_YEAR
        if col != "Sex"
    ] + [
        "Year",
        "Category",
    ]

    wide = (
        data.pivot_table(
            index=index_cols,
            columns="Sex",
            values="Count",
            aggfunc="first",
        )
        .reset_index()
    )

    if not {"Male", "Female"}.issubset(wide.columns):
        return pd.DataFrame(
            columns=ID + [
                "Category",
                "Count",
                "Rate",
            ]
        )

    # Require both components. Do not treat a missing value as zero.
    wide = wide.dropna(
        subset=["Male", "Female"]
    ).copy()

    wide["Count"] = (
        wide["Male"]
        + wide["Female"]
    )

    wide["Sex"] = "Total"

    # The source does not provide citizenship-specific rates.
    wide["Rate"] = pd.NA

    return wide[
        ID + [
            "Category",
            "Count",
            "Rate",
        ]
    ]


def add_shares_and_rates(
    data,
    totals,
    derive_missing_rates=True,
):
    """
    Calculate category shares for complete category profiles.

    Derive missing rates only where the available population denominator
    is appropriate. Missing categories are not converted to zero.
    """

    data = data[
        data["Category"] != "Total"
    ].copy()

    if data.empty:
        return pd.DataFrame(
            columns=OUTPUT_COLS
        )

    data = data.drop_duplicates(
        subset=ID + ["Category"],
        keep="first",
    )

    for flag in [
        "From_Subcategory",
        "Was_Imputed_Count",
        "Was_Imputed_Rate",
        "Was_Imputed",
    ]:
        if flag not in data.columns:
            data[flag] = False

        data[flag] = (
            data[flag]
            .fillna(False)
            .astype(bool)
        )

    group_cols = [
        "Iso3_code",
        "Year",
        "Sex",
    ]

    # A profile is complete only when every category in that profile
    # has a non-missing Count.
    complete_profile = data.groupby(
        group_cols
    )["Count"].transform(
        lambda values: values.notna().all()
    )

    category_sum = data.groupby(
        group_cols
    )["Count"].transform(
        lambda values: values.sum(
            min_count=len(values)
        )
    )

    data["Share_pct"] = (
        100
        * data["Count"]
        / category_sum
    ).where(
        complete_profile
        & (category_sum > 0)
    )

    # Join overall totals and population for the same country-year-sex.
    total_rows = totals[
        group_cols + [
            "Count",
            "Population",
        ]
    ].rename(
        columns={
            "Count": "Total_Count",
        }
    )

    data = data.merge(
        total_rows,
        on=group_cols,
        how="left",
        validate="many_to_one",
    )

    data["Rate"] = pd.to_numeric(
        data["Rate"],
        errors="coerce",
    )

    data["Rate_Derived"] = False

    if derive_missing_rates:

        can_derive = (
            data["Rate"].isna()
            & data["Count"].notna()
            & data["Population"].notna()
            & (data["Population"] > 0)
        )

        data.loc[
            can_derive,
            "Rate",
        ] = (
            data.loc[
                can_derive,
                "Count",
            ]
            / data.loc[
                can_derive,
                "Population",
            ]
            * 100_000
        )

        data.loc[
            can_derive,
            "Rate_Derived",
        ] = True

    data["Sum_vs_Total"] = (
        category_sum
        / data["Total_Count"]
    ).where(
        complete_profile
        & data["Total_Count"].notna()
        & (data["Total_Count"] != 0)
    )

    # Keep a stable output schema.
    for col in OUTPUT_COLS:
        if col not in data.columns:
            data[col] = pd.NA

    return data[
        OUTPUT_COLS
    ]


# ============================================================
# 5. BUILD DIMENSION DATASETS
# ============================================================

def build_dimension(
    wide,
    totals,
    raw_dimension,
    output_name,
):
    """Build one non-sex dimension dataset."""

    data = wide[
        wide["Dimension"] == raw_dimension
    ][
        ID + [
            "Category",
            "Count",
            "Rate",
        ]
    ].copy()

    if output_name == "citizenship":

        # Keep the original Male and Female citizenship rows.
        data = data[
            data["Sex"].isin(["Male", "Female"])
        ].copy()

        # Derive Total-sex citizenship counts by adding Male + Female.
        total_data = build_citizenship_total(data)

        # Preserve Male, Female, and derived Total rows.
        data = pd.concat(
            [
                data,
                total_data,
            ],
            ignore_index=True,
        )

    else:

        # Other dimension profiles use overall Total-sex rows.
        data = data[
            data["Sex"] == "Total"
        ].copy()

    data = collapse_subcategories(data)

    data = interpolate_panel(
        data,
        ID_NO_YEAR + ["Category"],
        ["Count", "Rate"],
    )

    # Citizenship rates are not source-provided; do not derive them.
    derive_rates = (
        output_name != "citizenship"
    )

    return add_shares_and_rates(
        data,
        totals,
        derive_missing_rates=derive_rates,
    )


def build_sex(wide, totals):
    """
    Build the victim-sex profile from the overall Total dimension.

    Male and Female are categories in this output.
    Their rates remain source-provided rates; do not derive them using
    the overall population denominator.
    """

    data = wide[
        (wide["Dimension"] == "Total")
        & (wide["Category"] == "Total")
        & wide["Sex"].isin(
            ["Male", "Female"]
        )
    ][
        ID + [
            "Count",
            "Rate",
        ]
    ].copy()

    data["Category"] = data["Sex"]

    # Represent the profile as a Total-sex group with Male/Female categories.
    data["Sex"] = "Total"

    data["From_Subcategory"] = False

    data = interpolate_panel(
        data,
        ID_NO_YEAR + ["Category"],
        ["Count", "Rate"],
    )

    return add_shares_and_rates(
        data,
        totals,
        derive_missing_rates=False,
    )


# ============================================================
# 6. COVERAGE AND DIAGNOSTICS
# ============================================================

def build_coverage(datasets):
    """
    One row per country and dimension.

    n_years counts years with a complete category-share profile.
    n_imputed_years counts complete country-years with any imputation.
    """

    rows = []

    for dimension_name, data in datasets.items():

        usable = data[
            (data["Sex"] == "Total")
            & data["Share_pct"].notna()
        ].copy()

        if usable.empty:
            continue

        country_year = (
            usable.groupby(
                [
                    "Iso3_code",
                    "Country",
                    "Year",
                ],
                as_index=False,
            )
            .agg(
                Was_Imputed=(
                    "Was_Imputed",
                    "any",
                ),
                Sum_vs_Total=(
                    "Sum_vs_Total",
                    "first",
                ),
            )
        )

        coverage = (
            country_year.groupby(
                [
                    "Iso3_code",
                    "Country",
                ],
                as_index=False,
            )
            .agg(
                first_year=("Year", "min"),
                latest_year=("Year", "max"),
                n_years=("Year", "nunique"),
                n_imputed_years=(
                    "Was_Imputed",
                    "sum",
                ),
            )
        )

        coverage["Dimension"] = dimension_name

        rows.append(coverage)

    if not rows:
        return pd.DataFrame(
            columns=[
                "Iso3_code",
                "Country",
                "first_year",
                "latest_year",
                "n_years",
                "n_imputed_years",
                "Dimension",
            ]
        )

    return pd.concat(
        rows,
        ignore_index=True,
    )


def validate_overall_rates(wide, rates):
    """Check that source-observed overall rates remain unchanged."""

    raw = wide[
        (wide["Dimension"] == "Total")
        & (wide["Category"] == "Total")
        & (wide["Sex"] == "Total")
    ][
        [
            "Iso3_code",
            "Year",
            "Rate",
        ]
    ].rename(
        columns={
            "Rate": "Raw_Rate",
        }
    )

    merged = rates.merge(
        raw,
        on=[
            "Iso3_code",
            "Year",
        ],
        how="left",
        validate="one_to_one",
    )

    observed = merged["Raw_Rate"].notna()

    imputed_rate = (
        merged["Was_Imputed_Rate"]
        .fillna(False)
    )

    checks = {
        "Observed rates unchanged": (
            (
                merged.loc[
                    observed,
                    "Rate",
                ]
                - merged.loc[
                    observed,
                    "Raw_Rate",
                ]
            )
            .abs()
            .lt(1e-9)
            .all()
        ),

        "No rate imputed where source rate was observed": (
            ~(imputed_rate & observed)
        ).all(),
    }

    print("\n========== OVERALL RATES ==========")

    print(
        "Countries:",
        rates["Iso3_code"].nunique(),
    )

    print(
        "Country-years with a rate:",
        rates["Rate"].notna().sum(),
    )

    print(
        "Rates imputed:",
        int(imputed_rate.sum()),
    )

    print(
        "Zero rates kept:",
        int((rates["Rate"] == 0).sum()),
    )

    print("\n========== OVERALL VALIDATION ==========")

    for name, passed in checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):
        raise AssertionError(
            "One or more overall rate validation checks failed."
        )


def print_dimension_diagnostics(datasets):

    print(
        "\n========== DIMENSION DATASETS (Sex = Total) =========="
    )

    for name, data in datasets.items():

        total_sex = data[
            data["Sex"] == "Total"
        ].copy()

        if total_sex.empty:
            print(
                f"{name:13s} no Total-sex rows"
            )
            continue

        country_year = (
            total_sex.groupby(
                [
                    "Iso3_code",
                    "Country",
                    "Year",
                ],
                as_index=False,
            )
            .agg(
                Has_Complete_Profile=(
                    "Share_pct",
                    lambda values: values.notna().all(),
                ),
                Any_Imputed=(
                    "Was_Imputed",
                    "any",
                ),
                Sum_vs_Total=(
                    "Sum_vs_Total",
                    "first",
                ),
            )
        )

        complete = country_year[
            country_year["Has_Complete_Profile"]
        ]

        within_2pct = (
            (
                complete["Sum_vs_Total"] - 1
            ).abs() < 0.02
        ).mean() if not complete.empty else float("nan")

        print(
            f"{name:13s} "
            f"countries={complete['Iso3_code'].nunique():4d}  "
            f"complete country-years={len(complete):4d}  "
            f"country-years with any imputation="
            f"{int(country_year['Any_Imputed'].sum()):4d}  "
            f"sum within 2% of total={within_2pct:.0%}"
        )

        print(
            f"{'':13s} categories: "
            f"{sorted(data['Category'].dropna().unique())}"
        )


# ============================================================
# 7. MAIN
# ============================================================

def main():

    wide = load_raw()

    totals = overall_totals(wide)

    rates = build_rates(totals)

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Overall rates used by the map and similar-rate country explorer.
    rates.to_csv(
        OUT_DIR / "rates.csv",
        index=False,
    )

    datasets = {
        "sex": build_sex(
            wide,
            totals,
        )
    }

    for raw_dimension, output_name in DIMENSIONS.items():

        datasets[output_name] = build_dimension(
            wide,
            totals,
            raw_dimension,
            output_name,
        )

    # Write each dimension dataset.
    for name, data in datasets.items():

        data.to_csv(
            OUT_DIR / f"{name}.csv",
            index=False,
        )

    coverage = build_coverage(
        datasets
    )

    coverage.to_csv(
        OUT_DIR / "coverage.csv",
        index=False,
    )

    validate_overall_rates(
        wide,
        rates,
    )

    print_dimension_diagnostics(
        datasets
    )

    print(
        f"\nSaved processed datasets to: "
        f"{OUT_DIR.resolve()}"
    )


if __name__ == "__main__":
    main()


from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# APP CONFIGURATION
# Set the page layout, data locations, year range, and shared visual style.
 
st.set_page_config(
    page_title="Beyond the Yellow Tape",
    page_icon="🌍",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

START_YEAR = 2015
END_YEAR = 2024

BG = "#110E12"
PANEL = "#231B20"
BURGUNDY = "#581824"
CRIMSON = "#D44B55"
TAPE = "#EBC34C"
TEXT = "#F2EDE6"
MUTED_TEXT = "#BDB1B3"
GRID = "#49363D"

COUNTRY_A_COLOR = "#00BFA6"
COUNTRY_B_COLOR = "#FF6B6B"

QUALITY_COLORS = {
    "Reported": "#8ED281",
    "Includes imputed": "#669B55",
    "Includes derived": "#9EAB89",
}

DIMENSION_FILES = {
    "Sex": "sex.csv",
    "Mechanism": "mechanism.csv",
    "Relationship": "relationship.csv",
    "Situational context": "context.csv",
    "Citizenship": "citizenship.csv",
}


# VISUAL THEME
# Keep the decorative redesign scoped to the app shell and native widgets.
st.markdown(
    f"""
    <style>
        :root {{
            --noir-bg: {BG};
            --noir-panel: {PANEL};
            --noir-burgundy: {BURGUNDY};
            --noir-crimson: {CRIMSON};
            --noir-tape: {TAPE};
            --noir-ivory: {TEXT};
            --noir-muted: {MUTED_TEXT};
        }}

        .stApp {{
            background: var(--noir-bg);
            color: var(--noir-ivory);
        }}

        [data-testid="stHeader"] {{
            background: var(--noir-bg);
        }}

        [data-testid="stSidebar"] {{
            background: var(--noir-panel);
            border-right: 1px solid var(--noir-burgundy);
        }}

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] label {{
            color: var(--noir-ivory);
        }}

        [data-testid="stMetric"] {{
            background: var(--noir-panel);
            border: 1px solid var(--noir-burgundy);
            border-radius: 4px;
            padding: 1rem;
        }}

        [data-testid="stMetricLabel"],
        [data-testid="stCaptionContainer"] {{
            color: var(--noir-muted);
        }}

        [data-testid="stSelectbox"] label,
        [data-testid="stCheckbox"] label {{
            color: var(--noir-ivory);
        }}

        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background: var(--noir-panel);
            border-color: var(--noir-crimson);
            color: var(--noir-ivory);
        }}

        .case-header {{
            background: var(--noir-burgundy);
            border: 1px solid var(--noir-crimson);
            padding: 1.5rem 2rem 1.35rem;
            margin: 0 0 0.1rem;
        }}

        .case-kicker {{
            color: var(--noir-tape);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.2em;
            margin-bottom: 0.35rem;
        }}

        .case-title {{
            color: var(--noir-ivory);
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 800;
            letter-spacing: 0.08em;
            line-height: 1;
            margin: 0;
        }}

        .case-subtitle {{
            color: var(--noir-muted);
            font-size: 1rem;
            margin: 0.75rem 0 0;
        }}

        .warning-tape {{
            align-items: center;
            background-color: var(--noir-tape);
            background-image: repeating-linear-gradient(
                -45deg,
                transparent 0,
                transparent 28px,
                var(--noir-bg) 28px,
                var(--noir-bg) 34px
            );
            color: var(--noir-bg);
            display: flex;
            font-size: 0.95rem;
            font-weight: 1000;
            justify-content: center;
            letter-spacing: 0.3em;
            margin-top: 0.45rem;
            min-height: 1.65rem;
            padding: 0.2rem 1rem;
            text-transform: uppercase;
        }}

        .warning-tape span {{
            background: var(--noir-tape);
            font-size: 1.15rem;
            font-weight: 1000;
            padding: 0.05rem 1rem;
        }}

        h1, h2, h3 {{
            color: var(--noir-ivory);
            letter-spacing: 0.03em;
        }}

        hr {{
            border-color: var(--noir-burgundy);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


 
# DATA LOADING
# Read the prepared CSV files and cache them so reruns are faster.
 

@st.cache_data
def load_csv(filename):
    """Load a processed CSV file, returning an empty frame if unavailable."""
    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


@st.cache_data
def load_all_data():
    """Load the main rate dataset and all dimension datasets."""
    rates = load_csv("rates.csv")

    dimensions = {
        name: load_csv(filename)
        for name, filename in DIMENSION_FILES.items()
    }

    return rates, dimensions


# Clean the overall-rate table and standardize its types and imputation flags.
def prepare_rates(data):
    """Standardize the overall rate dataset for dashboard use."""
    if data.empty:
        return pd.DataFrame()

    data = data.copy()

    required = ["Country", "Year", "Rate", "Count"]
    missing = [col for col in required if col not in data.columns]

    if missing:
        st.error(
            "The rates.csv file is missing required columns: "
            + ", ".join(missing)
        )
        return pd.DataFrame()

    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Rate"] = pd.to_numeric(data["Rate"], errors="coerce")
    data["Count"] = pd.to_numeric(data["Count"], errors="coerce")

    if "Was_Imputed" not in data.columns:
        data["Was_Imputed"] = False

    data["Was_Imputed"] = (
        data["Was_Imputed"]
        .fillna(False)
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )

    data = data.dropna(subset=["Country", "Year"])
    data["Year"] = data["Year"].astype(int)

    # The wrangle output is intended to contain total-sex overall rates.
    if "Sex" in data.columns:
        data = data[data["Sex"].astype(str).str.lower() == "total"].copy()

    # Avoid duplicate country-year records.
    data = data.drop_duplicates(
        subset=["Country", "Year"],
        keep="first",
    )

    return data.sort_values(["Country", "Year"]).reset_index(drop=True)


# Clean category-level tables and retain total-sex rows for profile analysis.
def prepare_dimension(data):
    """Standardize a processed category dataset."""
    if data.empty:
        return pd.DataFrame()

    data = data.copy()

    required = ["Country", "Year", "Category", "Count", "Share_pct"]
    missing = [col for col in required if col not in data.columns]

    if missing:
        return pd.DataFrame()

    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Count"] = pd.to_numeric(data["Count"], errors="coerce")
    data["Share_pct"] = pd.to_numeric(data["Share_pct"], errors="coerce")

    data = data.dropna(subset=["Country", "Year", "Category"])
    data["Year"] = data["Year"].astype(int)

    # These dimension datasets may contain male, female, and total-sex rows.
    # The profile comparisons use total-sex records.
    if "Sex" in data.columns:
        data = data[
            data["Sex"].astype(str).str.lower() == "total"
        ].copy()

    return data


# Label each rate so users can distinguish reported data from estimates.
def quality_label(row):
    """Return a readable quality label for a rate observation."""
    if bool(row.get("Was_Imputed", False)):
        return "Includes imputed"

    if bool(row.get("Rate_Derived", False)):
        return "Includes derived"

    return "Reported"


# Reuse one table renderer and handle empty tables safely.
def show_table(data, height=400):
    if data is None or data.empty:
        st.info("No data available to display.")
        return

    # Make a copy so the original data is not modified
    display_data = data.copy()

    # Convert unsupported object values to strings
    for col in display_data.columns:
        if display_data[col].dtype == "object":
            display_data[col] = display_data[col].astype(str)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        height=height,
    )


# Apply the dashboard theme consistently before rendering each Plotly chart.
def show_plot(fig, height=None):
    """Apply common plot styling and render a Plotly figure."""
    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(
            family="Arial",
            color=TEXT,
            size=12,
        ),
        title=dict(
            font=dict(size=19, color=TEXT),
            x=0.02,
            xanchor="left",
        ),
        margin=dict(l=15, r=15, t=60, b=15),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT),
        ),
    )

    fig.update_xaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,
        color=TEXT,
    )

    fig.update_yaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,
        color=TEXT,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True},
    )


def format_year(year):
    if pd.isna(year):
        return "Unavailable"

    return str(int(year))


 
# LOAD DATA
# Load and prepare all tables once for the dashboard sections below.
 

rates_raw, dimensions_raw = load_all_data()

df = prepare_rates(rates_raw)

dimensions = {
    name: prepare_dimension(data)
    for name, data in dimensions_raw.items()
}


 
# APP HEADER
# Introduce the dashboard and explain the source and treatment of missing data.
 

st.markdown(
    """
    <header class="case-header">
        <div class="case-kicker">GLOBAL HOMICIDE INVESTIGATION</div>
        <h1 class="case-title">BEYOND THE YELLOW TAPE</h1>
        <p class="case-subtitle">Investigating Global Homicide Rates</p>
    </header>
    <div class="warning-tape" aria-label="Warning">
        <span>WARNING</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    Explore intentional homicide rates across countries and years.
    Compare countries with similar rates, examine victim profiles, and
    investigate how homicide rates change over time.
    """
)

st.caption(
    "Data source: UNODC intentional homicide data. "
    "Missing values are not treated as zero. Values flagged as imputed "
    "are estimates rather than directly reported observations."
)

if df.empty:
    st.error(
        "The overall rate dataset could not be loaded. "
        "Check that data/processed/rates.csv exists and contains "
        "Country, Year, Rate, and Count columns."
    )
    st.stop()


 
available_years = sorted(df["Year"].dropna().unique().astype(int).tolist())

if not available_years:
    st.error("No usable years were found in rates.csv.")
    st.stop()

default_year = (
    END_YEAR if END_YEAR in available_years else available_years[-1]
)

# DASHBOARD TABS
# Keep the application header above both independent dashboard views.
global_tab, compare_tab = st.tabs(["Global Overview", "Compare Countries"])

with global_tab:
    # GLOBAL OVERVIEW
    # Summarize the selected year and show the geographic pattern of homicide rates.
 

    overview_year, overview_filter, overview_spacer = st.columns([1, 1, 4])

    with overview_year:
        global_year = st.selectbox(
            "Year",
            available_years,
            index=available_years.index(default_year),
            label_visibility="visible",
        )

    with overview_filter:
        global_exclude_imputed = st.checkbox(
            "Exclude imputed rates",
            value=False,
            key="global_exclude_imputed",
            help=(
                "When selected, country rates flagged as imputed are "
                "excluded from the global overview."
            ),
        )

    global_year_rows = df[df["Year"] == global_year].copy()

    if global_exclude_imputed:
        global_year_rows = global_year_rows[~global_year_rows["Was_Imputed"]].copy()

    global_rows = global_year_rows.dropna(subset=["Rate"]).copy()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Countries with rate data",
            f"{global_rows['Country'].nunique():,}",
        )

    with col2:
        st.metric(
            "Median country rate",
            (
                f"{global_rows['Rate'].median():.2f}"
                if not global_rows.empty
                else "n/a"
            ),
            help="Median homicide rate per 100,000 population.",
        )

    with col3:
        total_count = global_rows["Count"].sum(min_count=1)

        st.metric(
            "Sum of available homicide counts",
            (
                f"{total_count:,.0f}"
                if pd.notna(total_count)
                else "n/a"
            ),
            help=(
                "Sum across available country records. "
                "This is not necessarily a complete global total."
            ),
        )

    if global_rows.empty:
        st.info(f"No usable overall rates are available for {global_year}.")
    else:
        overview_tab, ranking_tab = st.tabs(
            ["Global Map", "Country Ranking"]
        )

        with overview_tab:
            map_data = global_rows.copy()

            map_data["Quality"] = map_data.apply(
                quality_label,
                axis=1,
            )

            map_data["Count_text"] = map_data["Count"].map(
                lambda value: (
                    f"{value:,.0f}" if pd.notna(value) else "Unavailable"
                )
            )

            color_max = map_data["Rate"].quantile(0.95)

            if pd.isna(color_max) or color_max <= 0:
                color_max = map_data["Rate"].max()

            if pd.isna(color_max) or color_max <= 0:
                color_max = 1

            fig_map = px.choropleth(
                map_data,
                locations="Iso3_code" if "Iso3_code" in map_data.columns else "Country",
                locationmode=(
                    "ISO-3" if "Iso3_code" in map_data.columns else None
                ),
                color="Rate",
                hover_name="Country",
                hover_data={
                    "Rate": ":.2f",
                    "Quality": True,
                    "Count_text": True,
                },
                color_continuous_scale=[
                    [0.00, "#FFE69A"],  
                    [0.20, "#FFB347"],  
                    [0.45, "#FF7043"],  
                    [0.70, "#F52B42"],  
                    [1.00, "#A90032"],
                ],
                range_color=(0, color_max),
                projection="natural earth",
                labels={
                    "Rate": "Homicides per 100,000",
                    "Quality": "Data quality",
                    "Count_text": "Homicide count",
                },
                title=f"Global Intentional Homicide Rates — {global_year}",
            )

            fig_map.update_geos(
                projection_type="natural earth",
                center=dict(lon=0, lat=0),
                projection_scale=1,
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#8A737B",
                coastlinewidth=0.5,
                showcountries=True,
                countrycolor="#8A737B",
                countrywidth=0.45,
                showland=True,
                landcolor="#30232B",
                showocean=True,
                oceancolor=BG,
                bgcolor=BG,
            )

            fig_map.update_layout(
                uirevision="global-map-orientation",
                height=650,
                paper_bgcolor=BG,
                plot_bgcolor=BG,
                font=dict(family="Arial", color=TEXT, size=13),
                title=dict(
                    font=dict(size=22, color=TEXT),
                    x=0.02,
                    xanchor="left",
                ),
                margin=dict(l=0, r=0, t=65, b=10),
                coloraxis_colorbar=dict(
                    title=dict(
                        text="Rate per<br>100,000",
                        font=dict(color=TEXT),
                    ),
                    tickfont=dict(color=TEXT),
                    thickness=14,
                    len=0.7,
                    outlinewidth=0,
                ),
            )

            show_plot(fig_map)

            st.caption(
                "The map uses a consistent color scale for the selected year, "
                "capped at the 95th percentile for visual contrast. Rates above "
                "the cap use the highest color. Imputed rates are estimates."
            )

            # # Aggregate category counts across countries to estimate each dimension's
            # # composition among the available records for this selected year.
            # st.subheader(f"World Victim-Profile Shares — {global_year}")
            # st.caption(
            #     "Each pie combines category counts across countries with data for "
            #     f"{global_year}. This is a world-level summary of available records, "
            #     "not a guaranteed complete global total; coverage differs by dimension."
            # )

            # world_dimension_names = [
            #     "Sex",
            #     "Mechanism",
            #     "Relationship",
            #     "Situational context",
            #     "Citizenship",
            # ]
            # world_pie_columns = st.columns(2)
            # world_pie_index = 0

            # for dimension_name in world_dimension_names:
            #     dimension_data = dimensions.get(dimension_name, pd.DataFrame())

            #     # Skip dimensions with no records for the selected year.
            #     if dimension_data.empty:
            #         continue

            #     selected_dimension = dimension_data[
            #         dimension_data["Year"] == global_year
            #     ].copy()

            #     if selected_dimension.empty:
            #         continue

            #     # Sum category counts across reporting countries, then calculate shares.
            #     world_counts = (
            #         selected_dimension.groupby("Category", as_index=False)["Count"]
            #         .sum(min_count=1)
            #         .dropna(subset=["Count"])
            #     )
            #     world_counts = world_counts[world_counts["Count"] >= 0]
            #     world_count_total = world_counts["Count"].sum()

            #     if world_counts.empty or world_count_total <= 0:
            #         continue

            #     world_counts["World share (%)"] = (
            #         world_counts["Count"] / world_count_total * 100
            #     )

            #     pie_figure = px.pie(
            #         world_counts,
            #         names="Category",
            #         values="Count",
            #         hole=0.35,
            #         title=dimension_name,
            #     )
            #     pie_figure.update_traces(
            #         textinfo="percent",
            #         hovertemplate=(
            #             "%{label}<br>Available count: %{value:,.0f}"
            #             "<br>Share: %{percent}<extra></extra>"
            #         ),
            #     )

            #     with world_pie_columns[world_pie_index % 2]:
            #         show_plot(pie_figure, 380)
            #     world_pie_index += 1

            # if world_pie_index == 0:
            #     st.info(
            #         f"No dimension breakdowns are available for {global_year}."
            #     )

        with ranking_tab:
            ranking = global_rows.sort_values(
                "Rate",
                ascending=False,
            ).head(20)

            fig_rank = px.bar(
                ranking.sort_values("Rate"),
                x="Rate",
                y="Country",
                orientation="h",
                color="Rate",
                color_continuous_scale="Reds",
                labels={
                    "Rate": "Homicides per 100,000 population",
                    "Country": "",
                },
                title=f"20 Highest Country Rates — {global_year}",
            )

            show_plot(fig_rank, 550)

            show_table(
                ranking[
                    [
                        "Country",
                        "Rate",
                        "Count",
                        "Was_Imputed",
                    ]
                ].rename(
                    columns={
                        "Rate": "Rate per 100,000",
                        "Count": "Homicide count",
                        "Was_Imputed": "Imputed",
                    }
                )
            )


 
with compare_tab:
    compare_year_column, compare_filter, compare_spacer = st.columns([1, 1, 4])

    with compare_year_column:
        compare_year = st.selectbox(
            "Year",
            available_years,
            index=available_years.index(default_year),
            key="compare_year",
        )

    with compare_filter:
        compare_exclude_imputed = st.checkbox(
            "Exclude imputed rates",
            value=False,
            key="compare_exclude_imputed",
            help=(
                "When selected, country rates flagged as imputed are "
                "excluded from country comparisons."
            ),
        )

    compare_year_rows = df[df["Year"] == compare_year].copy()

    if compare_exclude_imputed:
        compare_year_rows = compare_year_rows[
            ~compare_year_rows["Was_Imputed"]
        ].copy()

    # SIMILAR-RATE COUNTRY EXPLORER
    # Find countries whose selected-year rates are closest to the chosen country.


    st.header("Find Countries with Similar Homicide Rates")

    st.caption(
        f"Countries are matched using their homicide rates in {compare_year} "
        "only. Matches are ranked by the absolute difference in rates. "
        "No other year is substituted or averaged."
    )

    similar_rows = compare_year_rows.dropna(subset=["Rate"]).copy()

    if similar_rows.empty:
        st.info(
            f"No usable country rates are available for {compare_year} "
            "with the current settings."
        )
    else:
        similar_countries = sorted(
            similar_rows["Country"].dropna().unique().tolist()
        )

        selected_country = st.selectbox(
            "Choose a country",
            similar_countries,
            key="similar_rate_country",
        )

        selected_record = similar_rows[
            similar_rows["Country"] == selected_country
        ]

        if selected_record.empty:
            st.info("The selected country has no usable rate for this year.")
        else:
            selected_record = selected_record.iloc[0]
            selected_rate = float(selected_record["Rate"])

            st.metric(
                label=f"{selected_country} — {compare_year}",
                value=f"{selected_rate:.2f}",
                help="Intentional homicides per 100,000 population.",
            )

            if bool(selected_record["Was_Imputed"]):
                st.caption(
                    "This selected country rate is imputed and should be "
                    "interpreted as an estimate."
                )

            others = similar_rows[
                similar_rows["Country"] != selected_country
            ].copy()

            if others.empty:
                st.info("There are no other countries to compare.")
            else:
                others["Absolute difference"] = (
                    others["Rate"] - selected_rate
                ).abs()

                others["Ratio to selected"] = (
                    others["Rate"] / selected_rate
                    if selected_rate > 0
                    else np.nan
                )

                others["Quality"] = others.apply(
                    quality_label,
                    axis=1,
                )

                others = others.sort_values(
                    ["Absolute difference", "Country"]
                ).head(10)

                suggested_country = others["Country"].iloc[0]

                st.subheader("Closest matches")

                shown = others[
                    [
                        "Country",
                        "Rate",
                        "Ratio to selected",
                        "Absolute difference",
                        "Count",
                        "Quality",
                    ]
                ].copy()

                shown = shown.rename(
                    columns={
                        "Rate": "Homicide rate",
                        "Ratio to selected": "Ratio to selected (×)",
                        "Count": "Homicides (count)",
                    }
                )

                shown["Homicide rate"] = shown["Homicide rate"].round(2)
                shown["Ratio to selected (×)"] = (
                    shown["Ratio to selected (×)"].round(2)
                )
                shown["Absolute difference"] = (
                    shown["Absolute difference"].round(2)
                )

                show_table(shown)

                fig_similar = px.bar(
                    others.sort_values("Rate"),
                    x="Country",
                    y="Rate",
                    color="Quality",
                    color_discrete_map=QUALITY_COLORS,
                    labels={
                        "Rate": "Rate per 100,000",
                        "Quality": "Data quality",
                    },
                    title=f"Rate comparison around {selected_country}",
                )

                fig_similar.add_hline(
                    y=selected_rate,
                    line_dash="dash",
                    line_color=TEXT,
                    annotation_text=(
                        f"{selected_country}: {selected_rate:.2f}"
                    ),
                )

                show_plot(fig_similar, 420)


 
    # COUNTRY PROFILE COMPARISON
    # Compare category shares for two countries and view their annual rate histories.
 

    st.divider()
    st.header("Country Homicide Profile Comparison")

    st.caption(
        "Compare victim-sex and category profiles, alongside overall "
        "homicide-rate trends. Category shares describe the composition "
        "of victims, not individual risk."
    )

    all_countries = sorted(df["Country"].dropna().unique().tolist())

    if len(all_countries) < 2:
        st.info("At least two countries with data are needed for comparison.")
    else:
        default_a = (
            selected_country
            if "selected_country" in globals()
            and selected_country in all_countries
            else all_countries[0]
        )

        default_b = (
            suggested_country
            if "suggested_country" in globals()
            and suggested_country in all_countries
            and suggested_country != default_a
            else next(country for country in all_countries if country != default_a)
        )

        col_a, col_b = st.columns(2)

        with col_a:
            country_a = st.selectbox(
                "Select Country A",
                all_countries,
                index=all_countries.index(default_a),
                key="comparison_country_a",
            )

        with col_b:
            country_b = st.selectbox(
                "Select Country B",
                all_countries,
                index=all_countries.index(default_b),
                key="comparison_country_b",
            )

        colors = {
            country_a: COUNTRY_A_COLOR,
            country_b: COUNTRY_B_COLOR,
        }

        if country_a == country_b:
            st.warning("Please select two different countries.")
        else:
         
            # Country profile helper
         
            def get_profile(dimension_name, country, year):
                """Return profile rows for the exact requested year."""
                data = dimensions.get(dimension_name, pd.DataFrame())

                if data.empty:
                    return pd.DataFrame(
                        columns=["Category", "Share_pct"]
                    )

                rows = data[
                    (data["Country"] == country)
                    & (data["Year"] == year)
                ].copy()

                return rows[["Category", "Share_pct"]].reset_index(drop=True)

         
            # Female and NRI shares
         
            st.subheader("Female and Non-Resident Victim Shares")

            st.info(
                "These are shares of victims, not measures of risk. "
                "The available data does not provide group-specific population "
                "denominators, so these shares should not be interpreted as "
                "homicide rates for females or non-residents."
            )

            sex_data = dimensions.get("Sex", pd.DataFrame())
            citizenship_data = dimensions.get("Citizenship", pd.DataFrame())

            female_rows = []
            nri_rows = []

            for country in [country_a, country_b]:
                # Female share
                if not sex_data.empty:
                    sex_profile = get_profile(
                        "Sex",
                        country,
                        compare_year,
                    )

                    female_match = sex_profile[
                        sex_profile["Category"]
                        .astype(str)
                        .str.fullmatch(
                            r"(?i)female",
                            na=False,
                        )
                    ]

                    if not female_match.empty:
                        female_rows.append(
                            {
                                "Country": country,
                                "Female victim share (%)": float(
                                    female_match["Share_pct"].iloc[0]
                                ),
                            }
                        )

                # Non-resident / international categories
                if not citizenship_data.empty:
                    citizenship_profile = get_profile(
                        "Citizenship",
                        country,
                        compare_year,
                    )

                    category_text = (
                        citizenship_profile["Category"]
                        .astype(str)
                        .str.lower()
                    )

                    nri_match = citizenship_profile[
                        category_text.str.contains(
                            r"non.?resident|foreign|international",
                            regex=True,
                            na=False,
                        )
                    ]

                    if not nri_match.empty:
                        nri_rows.append(
                            {
                                "Country": country,
                                "NRI victim share (%)": float(
                                    nri_match["Share_pct"].sum()
                                ),
                            }
                        )

            female_frame = pd.DataFrame(female_rows)
            nri_frame = pd.DataFrame(nri_rows)

            share_col1, share_col2 = st.columns(2)

            with share_col1:
                if female_frame.empty:
                    st.info(
                        "Female victim-share data is unavailable "
                        "for one or both selected countries."
                    )
                else:
                    fig_female = px.bar(
                        female_frame,
                        x="Country",
                        y="Female victim share (%)",
                        color="Country",
                        color_discrete_map=colors,
                        text="Female victim share (%)",
                        title="Female victim share",
                    )

                    fig_female.update_traces(
                        texttemplate="%{text:.1f}%",
                        textposition="outside",
                    )

                    show_plot(fig_female, 400)

            with share_col2:
                if nri_frame.empty:
                    st.info(
                        "No matching non-resident/international categories "
                        "were found in the citizenship data for these countries."
                    )
                else:
                    fig_nri = px.bar(
                        nri_frame,
                        x="Country",
                        y="NRI victim share (%)",
                        color="Country",
                        color_discrete_map=colors,
                        text="NRI victim share (%)",
                        title="Non-resident / international victim share",
                    )

                    fig_nri.update_traces(
                        texttemplate="%{text:.1f}%",
                        textposition="outside",
                    )

                    show_plot(fig_nri, 400)


            # Dimension profile comparison


            st.subheader("Victim Profile by Dimension")

            dimension_choice = st.selectbox(
                "Choose profile dimension",
                [
                    "Mechanism",
                    "Relationship",
                    "Situational context",
                    "Citizenship",
                ],
                key="profile_dimension",
            )

            profile_a = get_profile(
                dimension_choice,
                country_a,
                compare_year,
            )

            profile_b = get_profile(
                dimension_choice,
                country_b,
                compare_year,
            )

            if profile_a.empty and profile_b.empty:
                st.info(
                    f"No {dimension_choice.lower()} profile data is available "
                    f"for {country_a} or {country_b} in {compare_year}."
                )
            else:
                profiles = profile_a.rename(
                    columns={"Share_pct": country_a}
                ).merge(
                    profile_b.rename(
                        columns={"Share_pct": country_b}
                    ),
                    on="Category",
                    how="outer",
                )

                profiles = profiles.sort_values(
                    by=[country_a, country_b],
                    ascending=False,
                    na_position="last",
                )

                plot_profiles = profiles.melt(
                    id_vars="Category",
                    var_name="Country",
                    value_name="Share (%)",
                ).dropna(subset=["Share (%)"])

                fig_profile = px.bar(
                    plot_profiles,
                    x="Category",
                    y="Share (%)",
                    color="Country",
                    barmode="group",
                    color_discrete_map=colors,
                    title=(
                        f"{dimension_choice} profile — "
                        f"{country_a} vs {country_b} ({compare_year})"
                    ),
                )

                fig_profile.update_layout(
                    xaxis_title="",
                    yaxis_title="Share of victims (%)",
                )

                show_plot(fig_profile, 460)

                display_profiles = profiles.copy()

                for country in [country_a, country_b]:
                    display_profiles[country] = display_profiles[country].map(
                        lambda value: (
                            "Not reported"
                            if pd.isna(value)
                            else f"{value:.1f}%"
                        )
                    )

                show_table(display_profiles)

                st.caption(
                    "'Not reported' means the category is absent from that "
                    "country's data. It is not equivalent to zero."
                )

         
            # Overall rate trend comparison
         
            st.subheader("Overall Homicide Rate Over Time")

            trend = df[
                df["Country"].isin([country_a, country_b])
            ].copy()

            if compare_exclude_imputed:
                trend = trend[~trend["Was_Imputed"]].copy()

            trend = trend.sort_values(["Country", "Year"])

            if trend.empty:
                st.info(
                    "No overall homicide-rate trend data is available "
                    "for these countries."
                )
            else:
                fig_trend = go.Figure()

                for country, color in [
                    (country_a, COUNTRY_A_COLOR),
                    (country_b, COUNTRY_B_COLOR),
                ]:
                    country_data = trend[
                        trend["Country"] == country
                    ].sort_values("Year")

                    if country_data.empty:
                        continue

                    fig_trend.add_trace(
                        go.Scatter(
                            x=country_data["Year"],
                            y=country_data["Rate"],
                            mode="lines+markers",
                            name=country,
                            line=dict(color=color, width=2),
                            marker=dict(size=7),
                            connectgaps=False,
                            customdata=country_data[
                                ["Was_Imputed"]
                            ].to_numpy(),
                            hovertemplate=(
                                "%{x}<br>"
                                "Rate: %{y:.2f}<br>"
                                "Imputed: %{customdata[0]}"
                                "<extra></extra>"
                            ),
                        )
                    )

                fig_trend.update_layout(
                    title="Annual intentional homicide rate",
                    xaxis_title="Year",
                    yaxis_title="Homicides per 100,000 population",
                )

                show_plot(fig_trend, 470)

                st.caption(
                    "Each point represents an annual rate. No moving average "
                    "or smoothing is applied. Missing years remain gaps in "
                    "the line rather than being treated as zero."
                )


 


with global_tab:
    # GLOBAL TRENDS
    # Show how rates and recorded counts change over time, while distinguishing a country median from a population-weighted global rate.
    st.divider()
    st.header("Global Homicide Trends")
    st.caption(
        "Annual trends use the available country-year observations. The median is a typical-country statistic; "
        "the count sum reflects only countries with available count data."
    )

    trend_data = df.dropna(subset=["Year", "Rate"]).copy()
    trend_data["Year"] = trend_data["Year"].astype(int)
    if global_exclude_imputed:
        trend_data = trend_data[~trend_data["Was_Imputed"]].copy()

    if trend_data.empty:
        st.info("No annual trend data is available with the current filters.")
    else:
        trend_summary = trend_data.groupby("Year", as_index=False).agg(
            Median_country_rate=("Rate", "median"),
            Countries_reporting=("Country", "nunique"),
            Available_homicide_count=("Count", lambda values: values.sum(min_count=1)),
        )
        trend_metric = st.selectbox(
            "Trend metric",
            ["Median country rate", "Available homicide count", "Countries reporting"],
            key="global_trend_metric",
        )
        metric_columns = {
            "Median country rate": ("Median_country_rate", "Median rate per 100,000"),
            "Available homicide count": ("Available_homicide_count", "Sum of available recorded homicide counts"),
            "Countries reporting": ("Countries_reporting", "Countries with usable rate data"),
        }
        metric_col, metric_label = metric_columns[trend_metric]
        fig_global_trend = px.line(
            trend_summary,
            x="Year",
            y=metric_col,
            markers=True,
            title=f"{trend_metric} by year",
            labels={metric_col: metric_label, "Year": "Year"},
        )
        show_plot(fig_global_trend, 420)
        show_table(trend_summary.rename(columns={
            "Median_country_rate": "Median rate per 100,000",
            "Countries_reporting": "Countries reporting",
            "Available_homicide_count": "Available homicide count sum",
        }))

        # A population-weighted global rate is only calculated if a population denominator is present.
        population_col = next((col for col in ["Population", "population", "Pop"] if col in trend_data.columns), None)
        if population_col:
            trend_data[population_col] = pd.to_numeric(trend_data[population_col], errors="coerce")
            weighted = trend_data.dropna(subset=["Count", population_col]).groupby("Year", as_index=False).agg(
                Total_homicides=("Count", "sum"), Total_population=(population_col, "sum")
            )
            weighted["Population-weighted rate per 100,000"] = (
                weighted["Total_homicides"] / weighted["Total_population"] * 100000
            )
            st.caption("A population-weighted rate is shown because the rates file includes a population denominator.")
            show_table(weighted)
        else:
            st.caption(
                "A true population-weighted global rate cannot be computed from the current rates file because no population denominator was found. "
                "The chart therefore reports country medians or available count sums, not a global rate."
            )


    # COUNTRY RATE CHANGE EXPLORER
    # Compare two selected years using observed endpoint records, and make the imputation status visible.
    st.divider()
    st.header("What Changed? Country Rate Explorer")
    st.caption(
        "Compare country rates between two years. Only countries with a usable rate at both selected endpoints are included; "
        "percentage changes from a zero baseline are undefined."
    )

    if len(available_years) >= 2:
        change_col1, change_col2 = st.columns(2)
        with change_col1:
            start_year = st.selectbox(
                "Starting year", available_years, index=0, key="rate_change_start_year"
            )
        with change_col2:
            end_year = st.selectbox(
                "Ending year", available_years, index=len(available_years)-1, key="rate_change_end_year"
            )

        if start_year == end_year:
            st.info("Choose two different years to compare change.")
        else:
            endpoint_data = df[df["Year"].isin([start_year, end_year])].copy()
            if global_exclude_imputed:
                endpoint_data = endpoint_data[~endpoint_data["Was_Imputed"]].copy()
            endpoint_data = endpoint_data.dropna(subset=["Rate"])
            start_rates = endpoint_data[endpoint_data["Year"] == start_year][["Country", "Rate", "Was_Imputed"]].rename(
                columns={"Rate": "Starting rate", "Was_Imputed": "Starting rate imputed"}
            )
            end_rates = endpoint_data[endpoint_data["Year"] == end_year][["Country", "Rate", "Was_Imputed"]].rename(
                columns={"Rate": "Ending rate", "Was_Imputed": "Ending rate imputed"}
            )
            changes = start_rates.merge(end_rates, on="Country", how="inner")
            if changes.empty:
                st.info("No countries have rates at both selected endpoints with the current filters.")
            else:
                changes["Absolute change"] = changes["Ending rate"] - changes["Starting rate"]
                changes["Percentage change"] = np.where(
                    changes["Starting rate"] > 0,
                    changes["Absolute change"] / changes["Starting rate"] * 100,
                    np.nan,
                )
                change_view = st.radio(
                    "Rank countries by", ["Largest increases", "Largest decreases"],
                    horizontal=True, key="rate_change_direction"
                )
                change_metric = st.selectbox(
                    "Change measure", ["Absolute change", "Percentage change"], key="rate_change_measure"
                )
                ordered = changes.sort_values(
                    change_metric, ascending=(change_view == "Largest decreases"), na_position="last"
                ).head(15)
                chart_data = ordered.sort_values(change_metric)
                fig_change = px.bar(
                    chart_data,
                    x=change_metric,
                    y="Country",
                    orientation="h",
                    color=change_metric,
                    color_continuous_scale="RdYlGn_r",
                    title=f"{change_view}: {start_year} to {end_year}",
                    labels={change_metric: change_metric, "Country": ""},
                )
                show_plot(fig_change, 520)
                show_table(ordered)
                st.caption(
                    "Positive values indicate an increase and negative values a decrease. Imputation flags identify estimated endpoint values; "
                    "these comparisons are descriptive and do not establish causes."
                )
    else:
        st.info("At least two distinct years are needed for a change comparison.")

#============================================================================
    # # DATA COVERAGE AND QUALITY EXPLORER
    # # Visualize country-year reporting gaps and compare the availability of each dimension dataset.
    # st.divider()
    # st.header("Data Coverage and Quality")
    # st.caption(
    #     "A missing observation is not a zero. This view shows coverage in the processed data and flags imputed overall rates."
    # )

    # coverage_data = df.copy()
    # coverage_data["Year"] = coverage_data["Year"].astype(int)
    # coverage_data["Coverage status"] = np.where(
    #     coverage_data["Was_Imputed"], "Imputed rate", "Reported rate"
    # )
    # coverage_data["Coverage code"] = np.where(coverage_data["Was_Imputed"], 2, 1)

    # coverage_pivot = coverage_data.pivot_table(
    #     index="Country", columns="Year", values="Coverage code", aggfunc="max"
    # )
    # coverage_pivot = coverage_pivot.reindex(columns=available_years)
    # if not coverage_pivot.empty:
    #     coverage_values = coverage_pivot.fillna(0).to_numpy()
    #     coverage_fig = go.Figure(data=go.Heatmap(
    #         z=coverage_values,
    #         x=[str(year) for year in coverage_pivot.columns],
    #         y=coverage_pivot.index.tolist(),
    #         zmin=0,
    #         zmax=2,
    #         colorscale=[[0, "#263642"], [0.5, "#4F8FC0"], [1, "#D5A34A"]],
    #         colorbar=dict(
    #             title="Status",
    #             tickvals=[0, 1, 2],
    #             ticktext=["Missing", "Reported", "Imputed"],
    #         ),
    #         hovertemplate="Country: %{y}<br>Year: %{x}<br>Status code: %{z}<extra></extra>",
    #     ))
    #     coverage_fig.update_layout(title="Country-year rate coverage", xaxis_title="Year", yaxis_title="Country", height=750)
    #     show_plot(coverage_fig, 750)
    #     st.caption("Heatmap legend: dark = no usable rate, blue = reported rate, gold = imputed rate.")

    # coverage_rows = []
    # for dim_name, dim_df in dimensions.items():
    #     if dim_df.empty:
    #         coverage_rows.append({"Dimension": dim_name, "Countries with data": 0, "Country-years": 0})
    #         continue
    #     selected_dim = dim_df[dim_df["Year"].isin(available_years)]
    #     coverage_rows.append({
    #         "Dimension": dim_name,
    #         "Countries with data": selected_dim["Country"].nunique(),
    #         "Country-years": selected_dim[["Country", "Year"]].drop_duplicates().shape[0],
    #     })
    # coverage_summary = pd.DataFrame(coverage_rows)
    # st.subheader("Dimension reporting coverage")
    # show_table(coverage_summary)
#============================================================================

with compare_tab:
    # EXPANDED MULTI-DIMENSION PROFILE COMPARISON
    # Let viewers inspect category distributions for both selected countries across all available dimensions in one place.
    st.divider()
    st.header("Compare Homicide Profiles Across Dimensions")
    st.caption(
        "This view compares the composition of recorded victims in each dimension. Category shares are not group-specific homicide risks, "
        "and unavailable categories should not be interpreted as zero."
    )

    # Reuse the countries selected in the main comparison section
    profile_country_a = country_a
    profile_country_b = country_b
    profile_year = compare_year

    if profile_country_a == profile_country_b:
        st.warning("Select two different countries to compare profiles.")
    else:
        combined_profile_rows = []
        for dim_name, dim_df in dimensions.items():
            if dim_df.empty:
                continue
            for country in [profile_country_a, profile_country_b]:
                country_dimension = dim_df[
                    (dim_df["Country"] == country) & (dim_df["Year"] == profile_year)
                ][["Category", "Share_pct"]].copy()
                if country_dimension.empty:
                    continue
                country_dimension["Dimension"] = dim_name
                country_dimension["Country"] = country
                combined_profile_rows.append(country_dimension)

        if not combined_profile_rows:
            st.info("No profile dimension data is available for this country pair and year.")
        else:
            all_profiles = pd.concat(combined_profile_rows, ignore_index=True)
            profile_dimension_filter = st.multiselect(
                "Dimensions to display",
                options=list(dimensions.keys()),
                default=[name for name in dimensions.keys() if name in all_profiles["Dimension"].unique()],
                key="all_dimension_filter",
            )
            visible_profiles = all_profiles[all_profiles["Dimension"].isin(profile_dimension_filter)]
            if visible_profiles.empty:
                st.info("Select at least one dimension with available data.")
            else:
                # Create one combined chart for all selected dimensions
                profile_chart = go.Figure()

                for country, color in [
                    (profile_country_a, COUNTRY_A_COLOR),
                    (profile_country_b, COUNTRY_B_COLOR),
                ]:
                    country_data = visible_profiles[
                        visible_profiles["Country"] == country
                    ].copy()

                    if country_data.empty:
                        continue

                    profile_chart.add_trace(
                        go.Bar(
                            # Multi-category X-axis:
                            # dimension first, individual category second
                            x=[
                                country_data["Dimension"].tolist(),
                                country_data["Category"].tolist(),
                            ],
                            y=country_data["Share_pct"],
                            name=country,
                            marker_color=color,
                            customdata=country_data[
                                ["Dimension", "Category"]
                            ].to_numpy(),
                            hovertemplate=(
                                "Dimension: %{customdata[0]}<br>"
                                "Category: %{customdata[1]}<br>"
                                "Share: %{y:.1f}%"
                                "<extra>%{fullData.name}</extra>"
                            ),
                        )
                    )

                profile_chart.update_layout(
                    title=(
                        f"Victim profile shares: {profile_country_a} "
                        f"vs {profile_country_b} ({profile_year})"
                    ),
                    barmode="group",
                    height=600,
                    bargap=0.2,
                    xaxis=dict(
                        title="",
                        type="multicategory",
                        tickfont=dict(size=10),
                        automargin=True,
                    ),
                    yaxis=dict(
                        title="Share of recorded victims (%)",
                        range=[0, 100],
                    ),
                )

                show_plot(profile_chart)
with compare_tab:
    # DATA QUALITY NOTES
    # Keep the key limitations and interpretation guidance visible to dashboard users.
 

    st.divider()

    with st.expander("Data quality and methodology notes"):
        st.markdown(
            """
            - **Rates:** Overall intentional homicide rates are expressed per
              100,000 population.
            - **Missing values:** Missing observations are not automatically
              treated as zero.
            - **Imputation:** The wrangle process may interpolate eligible
              internal gaps. Values flagged as imputed are estimates.
            - **Similar-rate explorer:** Countries are compared using the
              selected year only.
            - **Profiles:** Category shares describe the distribution of
              recorded victims within the available categories.
            - **Trends:** Annual rates are displayed without moving averages
              or smoothing.
            - **Comparability:** Differences in reporting practices,
              category coverage, and unknown classifications may affect
              cross-country comparisons.
            """
        )

    st.caption(
        "Beyond the Yellow Tape — Investigating Global Homicide Rates"
    )
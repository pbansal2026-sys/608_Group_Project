
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Beyond the Yellow Tape",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #242424;
    }

    [data-testid="stHeader"] {
        background-color: #242424;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    div.stButton > button {
        border: 1px solid #880808;
        border-radius: 0.4rem;
        color: #880808;
        font-weight: 600;
        height: 2.75rem;
    }

    div.stButton > button:hover,
    div.stButton > button:focus {
        border-color: #b22222;
        color: #b22222;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    return {
        "Counts": pd.read_csv(DATA_DIR / "TotalCounts.csv"),
        "Rate": pd.read_csv(DATA_DIR / "Total_Rate.csv"),
    }


datasets = load_data()

st.title("Beyond the Yellow Tape")
st.subheader("Global intentional homicide")

if "map_mode" not in st.session_state:
    st.session_state.map_mode = "Counts"

counts_button, rate_button = st.columns(2, gap="small")
with counts_button:
    if st.button("Counts", key="counts_button", width="stretch"):
        st.session_state.map_mode = "Counts"
with rate_button:
    if st.button("Rate", key="rate_button", width="stretch"):
        st.session_state.map_mode = "Rate"

mode = st.session_state.map_mode
df = datasets[mode]
years = sorted(df["Year"].dropna().unique())
map_data = df.dropna(subset=["Iso3_code", "VALUE", "Year"])
value_label = "Homicides per 100,000 people" if mode == "Rate" else "Homicide victims"

fig = px.choropleth(
    map_data,
    locations="Iso3_code",
    locationmode="ISO-3",
    color="VALUE",
    hover_name="Country",
    animation_frame="Year",
    animation_group="Iso3_code",
    color_continuous_scale=[
        [0.0, "#fff7bc"],
        [0.25, "#fee391"],
        [0.5, "#fec44f"],
        [0.75, "#f03b20"],
        [1.0, "#ff0000"],
    ],
    projection="natural earth",
    labels={
        "VALUE": value_label,
    },
    range_color=[map_data["VALUE"].min(), map_data["VALUE"].max()],
    title=f"Intentional homicide {mode.lower()}",
)

fig.update_geos(
    showframe=False,
    showcoastlines=True,
    coastlinecolor="#666666",
    landcolor="#3b3b3b",
    oceancolor="#242424",
    showocean=True,
    bgcolor="#242424",
    projection_rotation=dict(lon=0, lat=15, roll=0),
    projection_scale=1.05,
)

fig.update_layout(
    height=760,
    autosize=True,
    margin=dict(l=0, r=0, t=55, b=0),
    paper_bgcolor="#242424",
    plot_bgcolor="#242424",
    font=dict(color="#f2f2f2"),
    title=dict(x=0.5, xanchor="center"),
    coloraxis_colorbar=dict(
        title=dict(text=value_label, font=dict(color="#f2f2f2")),
        tickfont=dict(color="#f2f2f2"),
    ),
)

if fig.layout.sliders:
    fig.layout.sliders[0].active = len(years) - 1
    fig.layout.sliders[0].currentvalue = dict(prefix="Year: ")
    fig.layout.sliders[0].font = dict(color="#f2f2f2")
    fig.layout.sliders[0].pad = dict(t=12)
    fig.layout.sliders[0].bgcolor = "#3b3b3b"
    fig.layout.sliders[0].activebgcolor = "#880808"
    fig.layout.sliders[0].bordercolor = "#880808"

fig.layout.updatemenus = []

st.plotly_chart(
    fig,
    width="stretch",
    config={"responsive": True, "displaylogo": False},
)

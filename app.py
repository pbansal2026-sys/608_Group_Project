
import streamlit as st
import pandas as pd
import plotly.express as px

# Load your cleaned UNODC dataset
df = pd.read_csv("data/processed/TotalCounts.csv")

st.title("Beyond the Yellow Tape")
st.subheader("Global Intentional Homicide Rates")

# Let users choose a year
years = sorted(df["Year"].dropna().unique())

selected_year = st.select_slider(
    "Select a year",
    options=years,
    value=years[-1]
)

# Filter data for the selected year
map_data = df[df["Year"] == selected_year].dropna(
    subset=["Iso3_code", "VALUE"]
)

# Create the choropleth map
fig = px.choropleth(
    map_data,
    locations="Iso3_code",
    locationmode="ISO-3",
    color="VALUE",
    hover_name="Country",
    color_continuous_scale="YlOrRd",
    projection="natural earth",
    labels={
        "homicide_rate": "Homicides per 100,000"
    },
    title=f"Intentional Homicide Rates ({selected_year})"
)

fig.update_geos(
    showframe=False,
    showcoastlines=True
)

fig.update_layout(
    height=600,
    margin=dict(l=0, r=0, t=50, b=0)
)

st.plotly_chart(fig, width="stretch")

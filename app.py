#loading data
import streamlit as st

import pandas as pd

import geopandas as gpd

import plotly.express as px

detroit = gpd.read_file(
    "data/detroit_analysis.geojson"
)

resources = gpd.read_file(
    "data/resources_detroit.geojson"
)

st.set_page_config(
    layout="wide"
)

#Dashboard Title
st.title("Detroit Community Development Dashboard")

st.write(
"""
This dashboard explores relationships between
community resources and unemployment across Detroit.
"""
)

#Sidebar
st.sidebar.title("Dashboard Filters")

amenity = st.sidebar.selectbox(

    "Community Resource",

    ["All"] +

    sorted(resources["amenity"].unique())
)


#Unemployment Slider
minimum = float(
    detroit["unemployment_rate"].min()
)

maximum = float(
    detroit["unemployment_rate"].max()
)

rate = st.sidebar.slider(

    "Maximum Unemployment Rate",

    minimum,

    maximum,

    maximum
)

detroit = detroit[
    detroit["unemployment_rate"] <= rate
]

#Statistics
# Calculate metrics
total_resources = len(resources)
total_tracts = len(detroit)
avg_unemployment = detroit["unemployment_rate"].mean()
highest_unemployment = detroit["unemployment_rate"].max()

# Create four metric cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("🏫 Community Resources", f"{total_resources:,}")
col2.metric("🗺️ Census Tracts", f"{total_tracts:,}")
col3.metric("📉 Average Unemployment", f"{avg_unemployment:.2f}%")
col4.metric("⚠️ Highest Unemployment", f"{highest_unemployment:.2f}%")

st.divider()
#adding some dashboard instructions
st.info("""
### Dashboard Guide

Use the filters in the sidebar to explore Detroit's unemployment and community resources.

**How to use this dashboard**

- Select a community resource type from the sidebar.
- Adjust the unemployment slider to focus on specific neighborhoods.
- Hover over census tracts to view detailed statistics.
- Zoom and pan the map to inspect different areas.
- Enable **Show Underlying Data** to view the dataset used in this dashboard.
""")
st.divider()

#interactive choropleth map
st.subheader("Detroit Unemployment by Census Tract")

fig = px.choropleth_map(
    detroit,
    geojson=detroit.geometry,
    locations=detroit.index,
    color="unemployment_rate",

    center={
        "lat": 42.3314,
        "lon": -83.0458
    },
    zoom=10,
    
    hover_name="GEOID",

    hover_data={
        "labor_force": True,
        "unemployed": True,
        "resource_count": True,
        "unemployment_rate":":.2f"
    },

    labels={
        "GEOID": "Census Tract",
        "labor_force": "Labor Force",
        "unemployed": "Unemployed Residents",
        "resource_count": "Community Resources",
        "unemployment_rate": "Unemployment Rate (%)"
    }
    
)

fig.update_layout(
    margin=dict(
        l=0,
        r=0,
        t=30,
        b=0
    )
)

#adding some symbols of resources

colors = {
    "school": "green",
    "clinic": "orange",
    "hospital": "red",
    "place_of_worship": "blue"
}

legend_names = {
    "school": "Schools",
    "clinic": "Clinics",
    "hospital": "Hospitals",
    "place_of_worship": "Places of Worship"
}

for amenity, color in colors.items():

    subset = resources[
        resources["amenity"] == amenity
    ]

    fig.add_scattermap(
        lat=subset.geometry.y,
        lon=subset.geometry.x,
        mode="markers",

        marker=dict(
            size=4,
            color=color,
            opacity=0.75,
        ),

        text=subset["name"],

        name=legend_names[amenity],

        hovertemplate=(
            "<b>%{text}</b><br>"
            f"Type: {legend_names[amenity]}"
            "<extra></extra>"
        )
    )
    
#changing legend position
fig.update_layout(
    legend=dict(
        y=1,
        x=1.02
    ),
    coloraxis_colorbar=dict(
        title="Unemployment %",
        x=-0.08,
        thickness=15,
        len=0.7
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)



#under the map

resource_chart = (
    resources["amenity"]
    .value_counts()
    .sort_values(ascending=False)
    .reset_index()
)

resource_chart.columns = [
    "Amenity",
    "Count"
]

bar = px.bar(
    resource_chart,
    x="Amenity",
    y="Count",
    color="Count"
)

#unemployment histogram



hist = px.histogram(
    detroit,
    x="unemployment_rate",
    nbins=20,
    title=""
)


#showing raw data
show_data = st.sidebar.checkbox(
    "Show Underlying Data"
)

if show_data:

    st.subheader("Underlying Census Tract Data")

    st.dataframe(
        detroit.drop(
            columns="geometry"
        )
    )



#fixing some layout issues
st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Community Resources by Typen")
    st.plotly_chart(
        bar,
        use_container_width=True
    )

with right:
    st.subheader("Distribution of Census Tract Unemployment Rates")
    st.plotly_chart(
        hist,
        use_container_width=True
    )

st.divider()

#Top 10 Table
top10 = (
    detroit[
        [
            "GEOID",
            "unemployment_rate",
            "resource_count"
        ]
    ]
    .sort_values(
        "unemployment_rate",
        ascending=False
    )
    .head(10)
)

top10 = top10.rename(
    columns={
        "GEOID": "Census Tract",
        "unemployment_rate": "Unemployment Rate (%)",
        "resource_count": "Community Resources"
    }
)

st.dataframe(
    top10.style.format({
        "Unemployment Rate (%)": "{:.2f}"
    })
)
import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="EV Population Dashboard", layout="wide")

st.title("🚗 Electric Vehicle Population Dashboard")
st.markdown("Explore the adoption of electric vehicles in Washington State.")

# Load Data


@st.cache_data
def load_data():
    data = pd.read_csv('Electric_Vehicle_Population_Data_20260126.csv')
    # Parse Location for Map

    def parse_location(loc_str):
        try:
            clean_loc = loc_str.replace('POINT (', '').replace(')', '')
            parts = clean_loc.split(' ')
            return float(parts[1]), float(parts[0])  # lat, lon
        except:
            return None, None

    # Apply parsing (this might take a moment, so caching is key)
    # For speed in demo, let's just drop null locations for the map
    data = data.dropna(subset=['Vehicle Location'])
    # Optional: If the dataset is huge, sample it for the map
    # data = data.sample(n=10000)

    # We will just extract lat/lon for valid rows
    data['lat'] = data['Vehicle Location'].apply(
        lambda x: float(x.split(' ')[2][:-1]))
    data['lon'] = data['Vehicle Location'].apply(
        lambda x: float(x.split(' ')[1][1:]))

    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error("The dataset file was not found. Please ensure 'Electric_Vehicle_Population_Data_20260126.csv' is in the same directory.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_county = st.sidebar.multiselect(
    "Select County", options=df['County'].unique(), default=df['County'].unique()[:1])
selected_make = st.sidebar.multiselect(
    "Select Manufacturer", options=df['Make'].unique(), default=['TESLA', 'NISSAN', 'CHEVROLET'])
year_range = st.sidebar.slider("Select Model Year", int(
    df['Model Year'].min()), int(df['Model Year'].max()), (2010, 2024))

# Filter Logic
filtered_df = df[
    (df['County'].isin(selected_county)) &
    (df['Make'].isin(selected_make)) &
    (df['Model Year'].between(year_range[0], year_range[1]))
]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Vehicles", f"{len(filtered_df):,}")
col2.metric("Avg Electric Range",
            f"{filtered_df[filtered_df['Electric Range']>0]['Electric Range'].mean():.1f} mi")
bev_percent = (filtered_df['Electric Vehicle Type']
               == 'Battery Electric Vehicle (BEV)').mean() * 100
col3.metric("% BEV", f"{bev_percent:.1f}%")

# Visualizations
st.markdown("---")

# Row 1: Map and Growth
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Geographic Distribution")
    # Using simple scatter_geo or mapbox
    if not filtered_df.empty:
        fig_map = px.scatter_mapbox(filtered_df, lat="lat", lon="lon", color="Make",
                                    zoom=6, height=400, mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("No data to display on map.")

with col_right:
    st.subheader("EV Growth Over Time")
    growth_data = filtered_df.groupby(
        'Model Year').size().reset_index(name='Count')
    fig_growth = px.line(growth_data, x='Model Year', y='Count',
                         markers=True, title="Registrations by Year")
    st.plotly_chart(fig_growth, use_container_width=True)

# Row 2: Make Distribution and Range
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Top Models")
    top_models = filtered_df['Model'].value_counts().head(10).reset_index()
    top_models.columns = ['Model', 'Count']
    fig_bar = px.bar(top_models, x='Count', y='Model', orientation='h',
                     color='Count', title="Top 10 Models in Selection")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right2:
    st.subheader("Electric Range Distribution")
    # Filter 0 range for cleaner histogram
    range_data = filtered_df[filtered_df['Electric Range'] > 0]
    fig_hist = px.histogram(range_data, x="Electric Range", color="Electric Vehicle Type",
                            nbins=30, title="Range Distribution (Non-Zero)")
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")
st.markdown("### Data Source: Washington State Department of Licensing")
st.dataframe(filtered_df.head(100))

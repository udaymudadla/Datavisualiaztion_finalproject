import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="WA EV Intelligence Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. HIGH-CONTRAST UI CUSTOMIZATION
# Using a Deep Navy (#10141d) and Electric Blue (#00d4ff) for maximum visibility
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #10141d;
        color: #ffffff;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #1f2937;
    }

    /* Metric Card Styling - High Contrast */
    [data-testid="stMetric"] {
        background-color: #1a1f2c;
        border: 2px solid #00d4ff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }

    /* Text Colors */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    
    /* Fix for chart visibility */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA ENGINE


@st.cache_data
def load_data():
    df = pd.read_csv('Electric_Vehicle_Population_Data_20260126.csv')
    df['Model Year'] = pd.to_numeric(df['Model Year'], errors='coerce')
    df['Electric Range'] = pd.to_numeric(df['Electric Range'], errors='coerce')
    coords = df['Vehicle Location'].str.extract(
        r'POINT \((?P<Lon>.*) (?P<Lat>.*)\)')
    df['Lat'] = pd.to_numeric(coords['Lat'], errors='coerce')
    df['Lon'] = pd.to_numeric(coords['Lon'], errors='coerce')
    return df[df['State'] == 'WA'].copy()


df_wa = load_data()

# 4. SIDEBAR CONTROLS
with st.sidebar:
    st.title("⚡ Control Panel")
    st.markdown("---")
    make_selection = st.multiselect(
        "Select Manufacturers:",
        options=sorted(df_wa['Make'].unique()),
        default=['TESLA', 'NISSAN', 'CHEVROLET', 'RIVIAN', 'BMW']
    )
    year_range = st.slider("Select Year Horizon:", 1997, 2026, (2018, 2026))
    ev_type = st.radio("Technology Type:", ["All", "BEV", "PHEV"])

# Apply Filtering
filtered_df = df_wa[df_wa['Make'].isin(
    make_selection) & df_wa['Model Year'].between(year_range[0], year_range[1])]
if ev_type != "All":
    type_map = {
        "BEV": "Battery Electric Vehicle (BEV)", "PHEV": "Plug-in Hybrid Electric Vehicle (PHEV)"}
    filtered_df = filtered_df[filtered_df['Electric Vehicle Type']
                              == type_map[ev_type]]

# 5. DASHBOARD BODY
st.title("🚗 Washington EV Population Intelligence")
st.markdown("#### *Master Level Geospatial & Technical Analysis*")

# High-Visibility Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Fleet", f"{len(filtered_df):,}")
m2.metric("Mean Range",
          f"{filtered_df[filtered_df['Electric Range']>0]['Electric Range'].mean():.1f} mi")
m3.metric("Grid Utilities", f"{filtered_df['Electric Utility'].nunique()}")
m4.metric("Top Brand", filtered_df['Make'].mode()[
          0] if not filtered_df.empty else "N/A")

st.markdown("---")

# 6. ANALYTICS PANE
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Adoption Trajectory")
    fig1 = px.histogram(filtered_df, x="Model Year", color="Electric Vehicle Type",
                        template="plotly_dark", barmode='group',
                        color_discrete_sequence=["#00d4ff", "#7000ff"])
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("🔋 Technical Range Evolution")
    fig2 = px.scatter(filtered_df[filtered_df['Electric Range'] > 0],
                      x="Model Year", y="Electric Range", color="Make",
                      template="plotly_dark")
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)', font_color="#ffffff")
    st.plotly_chart(fig2, use_container_width=True)

# 7. GEOSPATIAL HEATMAP
st.subheader("🗺️ Geospatial Registration Density")
# Using Carto-Darkmatter for better contrast in dark mode
fig_map = px.density_mapbox(filtered_df.dropna(subset=['Lat', 'Lon']),
                            lat='Lat', lon='Lon', radius=8,
                            center=dict(lat=47.3, lon=-120.5), zoom=5.5,
                            mapbox_style="carto-darkmatter", height=600)
fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}, paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_map, use_container_width=True)

# 8. FOOTER
st.markdown("---")
st.markdown(
    f"🔗 **Explore Source Code:** [GitHub Repository](https://github.com/udaymudadla/Datavisualiaztion_finalproject)")

import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import time
import plotly.express as px

# ----------------------
# Load Data
# ----------------------
@st.cache_data
def load_data():
    file_path = "Meteorite_Landings.csv"  # <- Your CSV filename
    if not os.path.exists(file_path):
        st.error("CSV file not found. Please add 'nasa_meteorite_data.csv' in the same folder.")
        return None

    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Rename coordinates if needed
    if "lat" in df.columns and "lon" in df.columns:
        df = df.rename(columns={"lat": "reclat", "lon": "reclong"})
    elif "latitude" in df.columns and "longitude" in df.columns:
        df = df.rename(columns={"latitude": "reclat", "longitude": "reclong"})
    elif "geolocation" in df.columns:
        df[["reclat", "reclong"]] = df["geolocation"].str.strip("()").str.split(",", expand=True)
        df["reclat"] = pd.to_numeric(df["reclat"], errors="coerce")
        df["reclong"] = pd.to_numeric(df["reclong"], errors="coerce")

    # Drop missing coordinates
    df = df.dropna(subset=["reclat", "reclong"])

    # Fix year column
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"])
        df["year"] = df["year"].astype(int)

    return df

df = load_data()
if df is None:
    st.stop()

# ----------------------
# Restrict to last 20 valid years (<2025)
# ----------------------
valid_years = sorted([y for y in df["year"].unique() if y < 2025])
last_20_years = valid_years[-20:] if len(valid_years) >= 20 else valid_years

# ----------------------
# Tabs
# ----------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎞️ Simulation", "🖼️ Gallery", "🌑 Asteroid Threat Simulation"])

# ----------------------
# Dashboard Tab
# ----------------------
with tab1:
    st.header("🌍 Meteorite Landings Dashboard")

    year = st.slider("Select Year", int(min(last_20_years)), int(max(last_20_years)), int(max(last_20_years)))
    year_data = df[df["year"] == year]

    st.subheader(f"Data for {year} ({len(year_data)} meteorites)")
    st.write(year_data.head())

    if not year_data.empty:
        deck = pdk.Deck(
            map_style="light",  # ✅ light world map
            initial_view_state=pdk.ViewState(
                latitude=20,
                longitude=0,
                zoom=1,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=year_data.rename(columns={"reclat": "lat", "reclong": "lon"}),
                    get_position="[lon, lat]",
                    get_color="[255, 100, 0, 160]",
                    get_radius=50000,
                ),
            ],
        )
        st.pydeck_chart(deck)
    else:
        st.warning("No location data available for this year.")

# ----------------------
# Simulation Tab
# ----------------------
with tab2:
    st.header("🎞️ Meteorite Simulation (Last 20 Years)")

    play = st.checkbox("▶️ Play Simulation")
    speed = st.slider("Simulation Speed (seconds per year)", 0.2, 2.0, 1.0)

    # Placeholder for dynamic updates
    placeholder = st.empty()

    if play:
        for y in last_20_years:
            year_data = df[df["year"] == y]

            with placeholder.container():
                st.subheader(f"Year: {y} ({len(year_data)} meteorites)")

                if not year_data.empty:
                    deck = pdk.Deck(
                        map_style="light",
                        initial_view_state=pdk.ViewState(
                            latitude=20,
                            longitude=0,
                            zoom=1,
                            pitch=0,
                        ),
                        layers=[
                            pdk.Layer(
                                "ScatterplotLayer",
                                data=year_data.rename(columns={"reclat": "lat", "reclong": "lon"}),
                                get_position="[lon, lat]",
                                get_color="[255, 0, 0, 200]",
                                get_radius=50000,
                            ),
                        ],
                    )
                    st.pydeck_chart(deck)
                else:
                    st.warning(f"No data for year {y}.")
            time.sleep(speed)
    else:
        st.info("Click ▶️ Play Simulation to start.")


# ----------------------
# Gallery Tab
# ----------------------
with tab3:  
    st.header("Meteorite Gallery")

    image_urls = [
        "https://images-assets.nasa.gov/image/NHQ202508030001/NHQ202508030001~orig.jpg",
        "https://images-assets.nasa.gov/image/PIA05334/PIA05334~orig.jpg",
        "https://images-assets.nasa.gov/image/PIA03212/PIA03212~orig.jpg"
    ]

    for url in image_urls:
        st.image(url, caption="NASA Meteorite Image", use_container_width=True)


# ------------------------------
# Asteroid Threat Simulation
# ------------------------------

import folium
from streamlit_folium import st_folium
with tab4:
    st.title("☄️ Hypothetical Asteroid Impact Simulation")

    # --- Stage slider ---
    stage = st.slider(
        "🛰️ Choose Impact Stage",
        1, 4, 1,
        format="%d"
    )

    stages = {
        1: "Approach Phase: Asteroid approaching Earth at 20 km/s.",
        2: "Atmosphere Entry: Glowing fireball visible in the sky.",
        3: "Impact: Explosion equivalent to 1.2M megatons TNT.",
        4: "Aftermath: Crater formed, widespread fires, earthquake."
    }

    st.info(stages[stage])

    # --- Map first ---
    marker_styles = {
        1: {"color": "blue", "size": 10},
        2: {"color": "orange", "size": 15},
        3: {"color": "red", "size": 25},
        4: {"color": "black", "size": 20},
    }

    impact_location = pd.DataFrame({
        'lat': [24.9],
        'lon': [67.0],
        'name': [f"Stage {stage}: {stages[stage]}"]
    })

    fig = px.scatter_mapbox(
        impact_location,
        lat="lat",
        lon="lon",
        hover_name="name",
        zoom=5,
        height=400
    )
    fig.update_traces(
        marker=dict(
            color=marker_styles[stage]["color"],
            size=marker_styles[stage]["size"]
        )
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0, "t":0, "l":0, "b":0}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Stage-specific content ---
    if stage == 1:
        st.subheader("🔹 General Info")
        st.markdown("""
            - **Name:** Impactor-2025 (imaginary asteroid)  
            - **Type:** Stony asteroid (ordinary chondrite)  
            - **Density:** ~3,000 kg/m³  
            - **Shape:** Roughly spherical  
        """)

    elif stage == 2:
        st.subheader("🔹 Physical Properties")
        st.markdown("""
            - **Diameter:** 250 m  
            - **Radius:** 125 m  
            - **Volume:** ≈ 8.18 × 10⁶ m³  
            - **Mass:** ≈ 2.45 × 10¹⁰ kg  
        """)

    elif stage == 3:
        st.subheader("🔹 Impact Energy & Effects")

        st.markdown("""
        <div style="font-size:16px; line-height:1.6;">
        <b>Kinetic energy:</b> 4.9 × 10¹⁸ joules  
        <br><i>(≈ 1.2 million megatons of TNT)</i>  
        <br><b>Crater diameter:</b> ~3.5 km  
        <br><b>Crater depth:</b> ~0.7 km  
        <br><b>Blast wave:</b> Severe destruction up to 50 km radius  
        <br><b>Thermal radiation:</b> Fires up to 80 km away  
        <br><b>Earthquake equivalent:</b> Magnitude ~7.0  
        </div>
        """, unsafe_allow_html=True)
   

    elif stage == 4:
        st.subheader("🚀 Mitigation Scenarios")
        st.markdown("""
            **1. Early Detection:** More warning = more safe options.  
            **2. Deflection:** Kinetic impactor, gravity tractor, lasers.  
            **3. Breaking/Destroying:** Nuclear option (risky).  
            **4. Earth Protection:** Evacuation, shelters, cooperation.  
            **5. Long-term Safety:** Investment in planetary defense.  
        """)






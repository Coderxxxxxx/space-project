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

st.markdown("""
    <div style="text-align: center; background-color:#0e1117; padding:15px; border-radius:10px;">
        <h1 style="color:#FFFFFF;">Newterra</h1>
    </div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "🎞️ Through the Years Simulation", "🖼️ Gallery", "🌑 Meteor Threat Simulation", "💫 Interesting Facts", "📌 References and Credits"])

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
        "https://images-assets.nasa.gov/image/PIA03212/PIA03212~orig.jpg",
        "https://d2pn8kiwq2w21t.cloudfront.net/original_images/didymos_scale.jpg"
    ]

    for url in image_urls:
        st.image(url, caption="NASA Meteorite Image", use_container_width=True)
    
    video_urls = [
        "https://images-assets.nasa.gov/video/GSFC_20200227_M13565_Nightingale/GSFC_20200227_M13565_Nightingale~orig.mp4"
    ]

    for url in video_urls:
        st.video(url)

# ------------------------------
# Asteroid Threat Simulation
# ------------------------------

import folium
from streamlit_folium import st_folium
with tab4:
    st.title("☄️ Warning: A Meteor Impactor 2025 is predicted to approach Earth!")

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
        st.image("https://miro.medium.com/v2/resize:fit:2000/1*dGMQXE65Igs6Q61hT_tK1w.jpeg")
        st.subheader("🔹 General Info")
        st.markdown("""
            - **Name:** Impactor-2025 (imaginary asteroid)  
            - **Type:** Stony asteroid (ordinary chondrite)  
            - **Density:** ~3,000 kg/m³  
            - **Shape:** Roughly spherical  
        """)
        st.subheader("🔹 Solution")
        st.markdown("""
            **Early Detection:** Deflection missions like NASA's DART mission are planned for meteor's deflection        
        """)

    elif stage == 2:

        st.image("https://cdn.mos.cms.futurecdn.net/CL4ZHg7cZYNBnKBha8exaS.jpg.webp")

        st.subheader("🔹 Physical Properties")
        st.markdown("""
            - **Diameter:** 250 m  
            - **Radius:** 125 m  
            - **Volume:** ≈ 8.18 × 10⁶ m³  
            - **Mass:** ≈ 2.45 × 10¹⁰ kg  
        """)
        st.subheader("🔹 Solution")
        st.markdown("""
            **Late Detection:** Impact location and time estimation, emegency alerts and evacuation of critical areas        
        """)

    elif stage == 3:
        st.image("https://scitechdaily.com/images/Asteroid-Strike-Animation.gif")

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
        st.subheader("🔹 Solution")
        st.markdown("""
            **Explosion Scenerio:** Measurements of explosion's energy and shockwave impact, guiding emergency teams       
        """)
   

    elif stage == 4:

        st.image("https://astroedui18n-live-f4d80dfc7ba44a6283e91-64c3f57.divio-media.com/images/Crater.max-800x600.jpg")

        st.subheader("🚀 Mitigation Scenarios")
        st.markdown("""
            **1. Early Detection:** More warning = more safe options.  
            **2. Deflection:** Kinetic impactor, gravity tractor, lasers.  
            **3. Breaking/Destroying:** Nuclear option (risky).  
            **4. Earth Protection:** Evacuation, shelters, cooperation.  
            **5. Long-term Safety:** Investment in planetary defense.  
        """)
        st.subheader("🔹 Solution")
        st.markdown("""
            **Recovery Solutions:** Mapping affected areas using drones and satellites, information collection for future impact prediction       
        """)

# --------------------
# Interesting Facts
# --------------------

with tab5:
    st.title("Interesting Facts about Meteors")

    st.markdown("""
                **1. DART (Double Asteroid Redirection Test):** In 2022, NASA’s DART spacecraft deliberately crashed into the asteroid moonlet Dimorphos to test if a spacecraft could change an asteroid’s path. The impact successfully shortened its orbit, proving that kinetic impact can deflect a dangerous asteroid. This was the world’s first real planetary defense experiment.\n
                **2. Hera Mission (ESA + NASA Collaboration):** After the DART mission, the European Space Agency launched Hera to study the impact site in detail. It will measure the crater, debris, and internal structure of Dimorphos. The mission helps scientists confirm how effective DART’s deflection really was.\n
                **3. ATLAS (Asteroid Terrestrial-impact Last Alert System):** ATLAS is a network of robotic telescopes designed to find asteroids just days before they could hit Earth. It scans the sky every night and sends early warnings for possible impacts. This system helps protect people by giving evacuation time in case of late detection.\n
                **4. Pan-STARRS and NEOWISE Surveys:** Pan-STARRS (on Earth) and NEOWISE (in space) continuously scan the sky to detect and track near-Earth asteroids. They collect data about asteroid size, orbit, and brightness. These missions are key tools NASA uses for early detection and monitoring of threats.\n
                **5. LCROSS (Lunar Crater Observation and Sensing Satellite):** In 2009, NASA’s LCROSS mission intentionally crashed part of a rocket into a shadowed lunar crater to study the ejected material. Scientists discovered traces of water ice. Though it targeted the Moon, this controlled impact helped understand how crashes can reveal useful data — similar to meteor impact studies.\n
                **6. Ames Vertical Gun Range (Lab Impact Simulation):** At NASA’s Ames Research Center, the Vertical Gun Range is used to fire small projectiles at high speed to simulate meteor impacts. Scientists study how craters form and how materials behave under extreme force. It helps in designing better spacecraft protection and impact prediction models.\n
                **7. Chelyabinsk Meteor Study (2013):** In 2013, a large meteor exploded over Chelyabinsk, Russia. NASA and scientists worldwide analyzed satellite and seismic data from the event. The explosion helped researchers understand how airbursts form and how much damage such explosions can cause even without ground impact.\n
    """)
        
# -------------------------
# Referencing and Credits
# -------------------------

with tab6:
    st.title("References and Credits")

    st.subheader("References ")
    st.markdown("""
        - **Nasa's Meteor Dataset:** https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv\n
        - **Images URLs:** https://images-assets.nasa.gov/image/NHQ202508030001/NHQ202508030001~orig.jpg   https://images-assets.nasa.gov/image/PIA05334/PIA05334~orig.jpg   https://images-assets.nasa.gov/image/PIA03212/PIA03212~orig.jpg https://d2pn8kiwq2w21t.cloudfront.net/original_images/didymos_scale.jpg   https://miro.medium.com/v2/resize:fit:2000/1*dGMQXE65Igs6Q61hT_tK1w.jpeg   https://cdn.mos.cms.futurecdn.net/CL4ZHg7cZYNBnKBha8exaS.jpg.webp    https://scitechdaily.com/images/Asteroid-Strike-Animation.gif    https://astroedui18n-live-f4d80dfc7ba44a6283e91-64c3f57.divio-media.com/images/Crater.max-800x600.jpg\n
        - **Videos URLs:** https://images-assets.nasa.gov/video/GSFC_20200227_M13565_Nightingale/GSFC_20200227_M13565_Nightingale~orig.mp4\n                            
   """)

    st.subheader("Team Credits")
    st.markdown("""
       - Manha Waheed (Research Work)
       - Arzoo Mueen Nawaz (Research Work and ppt)
       - Kashaf Arif (Research Work)
       - Ayesha Zakaria (Research Work)
       - Sulaiman Baloch (Research Work)
       - Tooba Khalid (Web-app development)                                       
    """)




import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Meteorite Data Explorer (Demo)")

data = pd.read_csv("meteorites.csv")

st.subheader("Dataset Preview")
st.dataframe(data)

st.subheader("Filter by Year")
year = st.slider("Select Year", min_value=1990, max_value=2025, value= 2010)
filtered = data[data["year"] >= year]
st.write(f"Showing meteorites from {year} onwards: ")
st.dataframe(filtered)

st.subheader("Mass Distribution")
fig, ax = plt.subplots()
ax.hist(data["mass"], bins=5, color="orange", edgecolor="black")
ax.set_xlabel("Mass (kg)")
ax.set_ylabel("Count")
st.pyplot(fig)

st.subheader("Meteorite Landings on Map")
map_data = data[["lat", "long"]].rename(columns={"long": "lon"})
st.map(map_data, zoom=1)
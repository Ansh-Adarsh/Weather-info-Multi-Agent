import folium
import streamlit as st
from streamlit_folium import st_folium


def render_map(map_data: dict) -> None:
    if not map_data or not map_data.get("lat"):
        st.info("Ask about a city to see it on the map.")
        return

    lat = map_data["lat"]
    lon = map_data["lon"]
    city = map_data.get("city", "")
    temp = map_data.get("temperature", "")
    aqi_label = map_data.get("aqi_label", "")
    description = map_data.get("description", "")
    rain_prob = map_data.get("rain_probability", "")

    weather_map = folium.Map(
        location=[lat, lon],
        zoom_start=11,
        tiles="CartoDB positron",
    )

    popup_html = f"""
      <div style='font-family:Arial;padding:10px;min-width:180px'>
        <h4 style='margin:0 0 8px'>{city}</h4>
        <p style='margin:4px 0'>🌡 {temp}°C</p>
        <p style='margin:4px 0'>🌤 {description}</p>
        <p style='margin:4px 0'>💨 AQI: {aqi_label or 'N/A'}</p>
        <p style='margin:4px 0'>🌧 Rain: {rain_prob}%</p>
      </div>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=220),
        tooltip=f"{city} — {temp}°C",
        icon=folium.Icon(color="blue", icon="cloud", prefix="fa"),
    ).add_to(weather_map)

    aqi_color_map = {
        "Good": "green",
        "Fair": "yellow",
        "Moderate": "orange",
        "Poor": "red",
        "Very Poor": "darkred",
    }
    circle_color = aqi_color_map.get(aqi_label, "gray")
    folium.Circle(
        location=[lat, lon],
        radius=4000,
        color=circle_color,
        fill=True,
        fill_opacity=0.15,
        tooltip=f"AQI: {aqi_label or 'No data'}",
    ).add_to(weather_map)

    st_folium(weather_map, width=None, height=400, returned_objects=[])

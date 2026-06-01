import os

import requests
from dotenv import load_dotenv


AQI_LABELS = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}


def get_aqi(city: str) -> dict:
    if not city or city == "Unknown":
        return {"error": "City is missing or unknown"}

    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OPENWEATHER_API_KEY is missing"}

    try:
        geocode_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()

        results = geocode_data.get("results", [])
        if not results:
            return {"error": "City not found"}

        latitude = results[0]["latitude"]
        longitude = results[0]["longitude"]

        aqi_response = requests.get(
            "http://api.openweathermap.org/data/2.5/air_pollution",
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": api_key,
            },
            timeout=10,
        )
        aqi_response.raise_for_status()
        aqi_data = aqi_response.json()
        current = aqi_data["list"][0]
        aqi_index = int(current["main"]["aqi"])
        components = current["components"]

        return {
            "city": city,
            "aqi_index": aqi_index,
            "aqi_label": AQI_LABELS.get(aqi_index, "Unknown"),
            "pm2_5": float(components["pm2_5"]),
            "pm10": float(components["pm10"]),
        }
    except requests.RequestException:
        return {"error": "AQI service unavailable"}
    except (KeyError, TypeError, ValueError, IndexError):
        return {"error": "AQI response was incomplete or invalid"}

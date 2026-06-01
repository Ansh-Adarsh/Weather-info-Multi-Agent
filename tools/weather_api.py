import requests


def get_weather(city: str) -> dict:
    """Fetch current weather for a city using the free Open-Meteo APIs."""
    if not city or city == "Unknown":
        return {"error": "City is missing or unknown"}

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

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,apparent_temperature,"
                    "relative_humidity_2m,wind_speed_10m,weather_code"
                ),
            },
            timeout=10,
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        current = weather_data["current"]

        return {
            "city": city,
            "temperature": float(current["temperature_2m"]),
            "apparent_temperature": float(current["apparent_temperature"]),
            "humidity": int(current["relative_humidity_2m"]),
            "wind_speed": float(current["wind_speed_10m"]),
            "weather_code": int(current["weather_code"]),
        }
    except requests.RequestException:
        return {"error": "Weather service unavailable"}
    except (KeyError, TypeError, ValueError):
        return {"error": "Weather response was incomplete or invalid"}

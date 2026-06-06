import requests

from graph.state import AgentState


WMO_CODE_MAP = {
    0: "clear skies",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    51: "light drizzle",
    61: "light rain",
    63: "moderate rain",
    71: "light snow",
    80: "rain showers",
    95: "thunderstorm",
}


def get_city_coordinates(city: str) -> dict:
    if not city or city == "Unknown":
        return {"error": "Could not geocode city"}

    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            return {"error": "Could not geocode city"}

        result = results[0]
        return {
            "city": city,
            "lat": float(result["latitude"]),
            "lon": float(result["longitude"]),
            "country": result.get("country", ""),
            "timezone": result.get("timezone", ""),
        }
    except (requests.RequestException, KeyError, TypeError, ValueError):
        return {"error": "Could not geocode city"}


def build_map_data(state: AgentState) -> dict:
    city = state.get("city", "")
    coords = get_city_coordinates(city)
    if "error" in coords:
        return {}

    weather_data = state.get("weather_data", {})
    forecast_data = state.get("forecast_data", {})
    aqi_data = state.get("aqi_data", {})
    weather_code = weather_data.get("weather_code", 0)
    rain_probability = (
        forecast_data.get("days", [{}])[0].get("rain_probability", "")
        if forecast_data.get("days")
        else ""
    )

    return {
        "city": coords["city"],
        "lat": coords["lat"],
        "lon": coords["lon"],
        "temperature": weather_data.get("temperature", ""),
        "aqi_label": aqi_data.get("aqi_label", ""),
        "description": WMO_CODE_MAP.get(weather_code, "unknown conditions"),
        "rain_probability": rain_probability,
    }

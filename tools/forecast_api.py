import requests


def get_forecast(city: str) -> dict:
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

        forecast_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": "auto",
                "forecast_days": 7,
                "daily": (
                    "temperature_2m_max,temperature_2m_min,"
                    "precipitation_probability_max,weather_code"
                ),
            },
            timeout=10,
        )
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        daily = forecast_data["daily"]

        days = []
        for index, date in enumerate(daily["time"]):
            days.append(
                {
                    "date": str(date),
                    "max_temp": float(daily["temperature_2m_max"][index]),
                    "min_temp": float(daily["temperature_2m_min"][index]),
                    "rain_probability": int(daily["precipitation_probability_max"][index]),
                    "weather_code": int(daily["weather_code"][index]),
                }
            )

        return {"city": city, "days": days}
    except requests.RequestException:
        return {"error": "Forecast service unavailable"}
    except (KeyError, TypeError, ValueError, IndexError):
        return {"error": "Forecast response was incomplete or invalid"}

from tools.forecast_api import get_forecast


def forecast_tool(city: str) -> dict:
    """Reusable tool wrapper for 7-day forecast lookup."""
    return get_forecast(city)


from tools.weather_api import get_weather


def weather_tool(city: str) -> dict:
    """Reusable tool wrapper for current weather lookup."""
    return get_weather(city)


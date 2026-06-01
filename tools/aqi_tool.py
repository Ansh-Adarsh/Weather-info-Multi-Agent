from tools.aqi_api import get_aqi


def aqi_tool(city: str) -> dict:
    """Reusable tool wrapper for air-quality lookup."""
    return get_aqi(city)


import logging

from graph.state import AgentState
from schemas.weather_schema import WeatherSummary
from tools.weather_tool import weather_tool


logger = logging.getLogger(__name__)

WEATHER_CODE_MAP = {
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


def run_weather(state: AgentState) -> AgentState:
    city = state.get("city", "Unknown")
    result = weather_tool(city)

    if "error" in result:
        logger.warning("Weather lookup failed for %s: %s", city, result["error"])
        return {
            "weather_data": result,
            "weather_summary": WeatherSummary(city=city, error=result["error"]).model_dump(),
        }

    summary = WeatherSummary(
        city=city,
        temperature=result.get("temperature"),
        apparent_temperature=result.get("apparent_temperature"),
        humidity=result.get("humidity"),
        wind_speed=result.get("wind_speed"),
        condition=WEATHER_CODE_MAP.get(result.get("weather_code"), "unknown conditions"),
    ).model_dump()
    return {"weather_data": result, "weather_summary": summary}

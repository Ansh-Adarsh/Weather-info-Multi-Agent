import logging

from langchain_core.messages import HumanMessage

from graph.state import AgentState
from prompts.recommendation_prompt import RECOMMENDATION_PROMPT
from schemas.recommendation_schema import RecommendationOutput


logger = logging.getLogger(__name__)


def _format_weather(data: dict) -> str:
    if not data or "error" in data:
        error = data.get("error", "unavailable") if data else "unavailable"
        return f"Current weather data is unavailable ({error})."
    return (
        f"{data.get('temperature', '?')} degrees C "
        f"(feels like {data.get('apparent_temperature', '?')} degrees C), "
        f"humidity {data.get('humidity', '?')}%, "
        f"wind {data.get('wind_speed', '?')} km/h."
    )


def _format_forecast(data: dict) -> str:
    if not data or "error" in data:
        error = data.get("error", "unavailable") if data else "unavailable"
        return f"Forecast data is unavailable ({error})."

    days = data.get("days", [])[:5]
    if not days:
        return "No forecast days available."

    return "\n".join(
        (
            f"  {day.get('date', '?')}: "
            f"{day.get('min_temp', '?')}-{day.get('max_temp', '?')} degrees C, "
            f"{day.get('rain_probability', '?')}% rain chance"
        )
        for day in days
    )


def _format_aqi(data: dict) -> str:
    if not data or "error" in data:
        error = data.get("error", "unavailable") if data else "unavailable"
        return f"Air quality data is unavailable ({error})."
    return (
        f"AQI index: {data.get('aqi_index', '?')} "
        f"({data.get('aqi_label', 'Unknown')}), "
        f"PM2.5: {data.get('pm2_5', '?')} micrograms/m3, "
        f"PM10: {data.get('pm10', '?')} micrograms/m3."
    )


def _build_observations(state: AgentState) -> str:
    """Include only the sources that the selected route was expected to fetch."""
    city = state.get("city", "Unknown")
    intent = state.get("intent", "")
    sections = [
        f"User Query: {state['user_query']}",
        f"City: {city}",
    ]

    if intent in {"weather", "combined"}:
        sections.append(
            f"\nCurrent Weather:\n  {_format_weather(state.get('weather_data', {}))}"
        )
    if intent in {"forecast", "combined"}:
        sections.append(
            f"\nForecast (upcoming days):\n"
            f"{_format_forecast(state.get('forecast_data', {}))}"
        )
    if intent in {"aqi", "combined"}:
        sections.append(
            f"\nAir Quality:\n  {_format_aqi(state.get('aqi_data', {}))}"
        )

    sections.append(
        "\nImportant: Sources not listed above were not requested. "
        "Do not describe them as unavailable or failed."
    )
    return "\n".join(sections)


def _fallback_output(state: AgentState) -> RecommendationOutput:
    city = state.get("city", "Unknown")
    intent = state.get("intent", "")
    weather = state.get("weather_data", {})
    forecast = state.get("forecast_data", {})
    aqi = state.get("aqi_data", {})
    parts: list[str] = []

    if intent in {"weather", "combined"}:
        if weather and "error" not in weather:
            parts.append(
                f"{city} is currently {weather.get('temperature', '?')} degrees C "
                f"and feels like "
                f"{weather.get('apparent_temperature', '?')} degrees C."
            )
        else:
            parts.append(f"Unable to fetch current weather for {city}.")

    if intent in {"forecast", "combined"}:
        if forecast and "error" not in forecast:
            first_day = forecast.get("days", [{}])[0]
            parts.append(
                f"The next forecast period ranges from "
                f"{first_day.get('min_temp', '?')} to "
                f"{first_day.get('max_temp', '?')} degrees C, with a "
                f"{first_day.get('rain_probability', '?')}% chance of rain."
            )
        else:
            parts.append(f"Unable to fetch the forecast for {city}.")

    if intent in {"aqi", "combined"}:
        if aqi and "error" not in aqi:
            parts.append(f"Air quality is {aqi.get('aqi_label', 'unknown')}.")
        else:
            parts.append("Air quality data is currently unavailable.")

    if not parts:
        parts.append(f"I could not fetch reliable weather intelligence for {city}.")

    return RecommendationOutput(
        summary=" ".join(parts),
        advice="Check local conditions before making outdoor plans.",
        risk_level="unknown",
    )


def run_recommendation(state: AgentState) -> AgentState:
    observations = _build_observations(state)
    prompt = f"{RECOMMENDATION_PROMPT}\n\nWeather Intelligence:\n{observations}"

    try:
        from agents.llm import llm

        structured_llm = llm.with_structured_output(RecommendationOutput)
        output = structured_llm.invoke([HumanMessage(content=prompt)])
    except Exception:
        logger.exception("Recommendation LLM call failed; using fallback.")
        output = _fallback_output(state)

    final_response = f"{output.summary} {output.advice}".strip()
    state["risk_level"] = output.risk_level
    state["final_response"] = final_response
    state["reasoning_trace"] = [
        *state.get("reasoning_trace", []),
        {
            "thought": "Synthesize weather intelligence into user-facing guidance.",
            "action": "generate_recommendation",
            "observation": f"risk_level={output.risk_level}",
        },
    ]
    state["messages"] = [
        *state.get("messages", []),
        {"role": "user", "content": state["user_query"]},
        {"role": "assistant", "content": final_response},
    ]
    return state

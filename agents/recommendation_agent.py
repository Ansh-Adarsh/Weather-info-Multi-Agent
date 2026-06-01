import logging

from langchain_core.messages import HumanMessage

from graph.state import AgentState
from prompts.recommendation_prompt import RECOMMENDATION_PROMPT
from schemas.recommendation_schema import RecommendationOutput

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Observation builder — produces human-readable context for the LLM
# ---------------------------------------------------------------------------

def _format_weather(data: dict) -> str:
    """Format current weather data into a readable summary."""
    if not data or "error" in data:
        error = data.get("error", "unavailable") if data else "unavailable"
        return f"Current weather data is unavailable ({error})."
    return (
        f"{data.get('temperature', '?')}°C (feels like {data.get('apparent_temperature', '?')}°C), "
        f"humidity {data.get('humidity', '?')}%, "
        f"wind {data.get('wind_speed', '?')} km/h."
    )


def _format_forecast(data: dict) -> str:
    """Format forecast data into a readable multi-day summary."""
    if not data or "error" in data:
        error = data.get("error", "unavailable") if data else "unavailable"
        return f"Forecast data is unavailable ({error})."
    days = data.get("days", [])[:5]
    if not days:
        return "No forecast days available."
    lines = []
    for day in days:
        lines.append(
            f"  {day.get('date', '?')}: "
            f"{day.get('temp_min', '?')}–{day.get('temp_max', '?')}°C, "
            f"{day.get('rain_probability', '?')}% rain chance"
        )
    return "\n".join(lines)


def _format_aqi(data: dict) -> str:
    """Format AQI data into a readable summary."""
    if not data or "error" in data:
        error = data.get("error", "unavailable") if data else "unavailable"
        return f"Air quality data is unavailable ({error})."
    return (
        f"AQI index: {data.get('aqi_index', '?')} ({data.get('aqi_label', 'Unknown')}), "
        f"PM2.5: {data.get('pm2_5', '?')} µg/m³, "
        f"PM10: {data.get('pm10', '?')} µg/m³."
    )


def _build_observations(state: AgentState) -> str:
    """Build a clean, human-readable observation block for the LLM."""
    city = state.get("city", "Unknown")
    sections = [
        f"User Query: {state['user_query']}",
        f"City: {city}",
        f"\nCurrent Weather:\n  {_format_weather(state.get('weather_data'))}",
        f"\nForecast (upcoming days):\n{_format_forecast(state.get('forecast_data'))}",
        f"\nAir Quality:\n  {_format_aqi(state.get('aqi_data'))}",
    ]
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Deterministic fallback — used when the LLM is unavailable
# ---------------------------------------------------------------------------

def _fallback_output(state: AgentState) -> RecommendationOutput:
    """Produce a basic recommendation without the LLM."""
    city = state.get("city", "Unknown")
    weather = state.get("weather_data", {})
    aqi = state.get("aqi_data", {})
    parts: list[str] = []

    if weather and "error" not in weather:
        parts.append(
            f"{city} is currently {weather.get('temperature', '?')}°C "
            f"and feels like {weather.get('apparent_temperature', '?')}°C."
        )
    elif weather:
        parts.append(f"Unable to fetch current weather for {city}.")

    if aqi and "error" not in aqi:
        parts.append(f"Air quality is {aqi.get('aqi_label', 'unknown')}.")
    elif aqi:
        parts.append("Air quality data is currently unavailable.")

    if not parts:
        parts.append(f"I could not fetch reliable weather intelligence for {city}.")

    return RecommendationOutput(
        summary=" ".join(parts),
        advice="Check local conditions before making outdoor plans.",
        risk_level="unknown",
    )


# ---------------------------------------------------------------------------
# Main recommendation node
# ---------------------------------------------------------------------------

def run_recommendation(state: AgentState) -> AgentState:
    """LLM-powered recommendation agent using structured output."""
    observations = _build_observations(state)
    prompt = (
        f"{RECOMMENDATION_PROMPT}\n\n"
        f"Weather Intelligence:\n{observations}"
    )

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

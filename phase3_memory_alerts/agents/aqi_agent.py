from graph.state import AgentState
from schemas.weather_schema import AQISummary
from tools.aqi_tool import aqi_tool


def run_aqi(state: AgentState) -> AgentState:
    city = state.get("city", "Unknown")
    result = aqi_tool(city)

    if "error" in result:
        return {
            "aqi_data": result,
            "aqi_summary": AQISummary(city=city, error=result["error"]).model_dump(),
        }

    summary = AQISummary(
        city=city,
        aqi_index=result.get("aqi_index"),
        aqi_label=result.get("aqi_label", "Unknown"),
        pm2_5=result.get("pm2_5"),
        pm10=result.get("pm10"),
    ).model_dump()
    return {"aqi_data": result, "aqi_summary": summary}

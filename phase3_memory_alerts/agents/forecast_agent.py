from graph.state import AgentState
from tools.forecast_tool import forecast_tool


def run_forecast(state: AgentState) -> AgentState:
    return {"forecast_data": forecast_tool(state.get("city", "Unknown"))}

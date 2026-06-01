from langgraph.graph import END, START, StateGraph

from agents.aqi_agent import run_aqi
from agents.conversation_agent import run_conversation
from agents.forecast_agent import run_forecast
from agents.recommendation_agent import run_recommendation
from agents.router import detect_intent
from agents.weather_agent import run_weather
from graph.state import AgentState


def route_after_router(state: AgentState) -> str | list[str]:
    agents = state.get("required_agents", [])
    if state.get("intent") == "combined":
        return ["weather_agent", "aqi_agent"]
    if agents:
        return agents[0]
    return "conversation_agent"


workflow = StateGraph(AgentState)
workflow.add_node("router", detect_intent)
workflow.add_node("conversation_agent", run_conversation)
workflow.add_node("weather_agent", run_weather)
workflow.add_node("forecast_agent", run_forecast)
workflow.add_node("aqi_agent", run_aqi)
workflow.add_node("recommendation_agent", run_recommendation)

workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "conversation_agent": "conversation_agent",
        "weather_agent": "weather_agent",
        "forecast_agent": "forecast_agent",
        "aqi_agent": "aqi_agent",
    },
)
workflow.add_edge("conversation_agent", END)
workflow.add_edge("weather_agent", "recommendation_agent")
workflow.add_edge("forecast_agent", "recommendation_agent")
workflow.add_edge("aqi_agent", "recommendation_agent")
workflow.add_edge("recommendation_agent", END)

app = workflow.compile()

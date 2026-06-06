from langgraph.graph import END, START, StateGraph

from agents.aqi_agent import run_aqi
from agents.conversation_agent import run_conversation
from agents.forecast_agent import run_forecast
from agents.memory_agent import run_memory
from agents.recommendation_agent import run_recommendation
from agents.router import detect_intent
from agents.weather_agent import run_weather
from graph.state import AgentState


def route_after_router(state: AgentState) -> str | list[str]:
    if state.get("intent") == "memory":
        return "memory_agent"
    agents = state.get("required_agents", [])
    if state.get("intent") == "combined":
        return ["weather_agent", "aqi_agent"]
    if agents:
        return agents[0]
    return "conversation_agent"


def save_response_node(state: AgentState) -> AgentState:
    from memory import database
    from tools.map_utils import build_map_data

    user_id = state.get("user_id", "default_user")

    if state.get("intent") != "memory":
        database.save_message(
            user_id,
            "user",
            state.get("user_query", ""),
            state.get("intent", ""),
            state.get("city", ""),
        )
        database.upsert_session(user_id)

    database.save_message(
        user_id,
        "assistant",
        state["final_response"],
        state.get("intent", ""),
        state.get("city", ""),
    )

    if state.get("city") and state["city"] != "Unknown":
        database.save_preference(user_id, last_city=state["city"])

    state["map_data"] = build_map_data(state)
    return state


workflow = StateGraph(AgentState)
workflow.add_node("router", detect_intent)
workflow.add_node("conversation_agent", run_conversation)
workflow.add_node("weather_agent", run_weather)
workflow.add_node("forecast_agent", run_forecast)
workflow.add_node("aqi_agent", run_aqi)
workflow.add_node("memory_agent", run_memory)
workflow.add_node("recommendation_agent", run_recommendation)
workflow.add_node("save_response_node", save_response_node)

workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    route_after_router,
    {
        "conversation_agent": "conversation_agent",
        "weather_agent": "weather_agent",
        "forecast_agent": "forecast_agent",
        "aqi_agent": "aqi_agent",
        "memory_agent": "memory_agent",
    },
)
workflow.add_edge("memory_agent", "save_response_node")
workflow.add_edge("conversation_agent", "save_response_node")
workflow.add_edge("weather_agent", "recommendation_agent")
workflow.add_edge("forecast_agent", "recommendation_agent")
workflow.add_edge("aqi_agent", "recommendation_agent")
workflow.add_edge("recommendation_agent", "save_response_node")
workflow.add_edge("save_response_node", END)

app = workflow.compile()

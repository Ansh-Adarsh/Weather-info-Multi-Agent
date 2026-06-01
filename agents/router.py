import logging

from langchain_core.messages import HumanMessage

from graph.state import AgentState
from prompts.router_prompt import ROUTER_PROMPT
from schemas.router_schema import RouterDecision

logger = logging.getLogger(__name__)


VALID_INTENTS = {"weather", "forecast", "aqi", "combined", "chat"}

INTENT_TO_AGENTS = {
    "weather": ["weather_agent"],
    "forecast": ["forecast_agent"],
    "aqi": ["aqi_agent"],
    "combined": ["weather_agent", "aqi_agent"],
    "chat": ["conversation_agent"],
}


def _safe_fallback_decision() -> RouterDecision:
    return RouterDecision(
        thought="The LLM router was unavailable, so the safest route is normal conversation.",
        intent="chat",
        city="",
        required_agents=["conversation_agent"],
    )


def _format_recent_messages(state: AgentState) -> str:
    messages = state.get("messages", [])[-4:]
    if not messages:
        return "None"
    return "\n".join(
        f"{message.get('role', 'unknown')}: {message.get('content', '')}"
        for message in messages
    )


def _normalize_decision(decision: RouterDecision, previous_city: str) -> RouterDecision:
    intent = decision.intent if decision.intent in VALID_INTENTS else "chat"
    city = decision.city.strip()

    if intent == "chat":
        city = ""
    elif not city:
        city = previous_city or "Unknown"

    return RouterDecision(
        thought=decision.thought,
        intent=intent,
        city=city.title() if city and city != "Unknown" else city,
        required_agents=INTENT_TO_AGENTS[intent],
    )


def detect_intent(state: AgentState) -> AgentState:
    query = state["user_query"]
    previous_city = state.get("previous_city", "")
    recent_messages = _format_recent_messages(state)

    try:
        from agents.llm import llm

        structured_llm = llm.with_structured_output(RouterDecision)
        prompt = (
            f"{ROUTER_PROMPT}\n\n"
            "Return a JSON-compatible object that matches the RouterDecision schema.\n"
            f"Recent conversation:\n{recent_messages}\n"
            f"User query: {query}\n"
            f"Previous city: {previous_city or 'None'}"
        )
        decision = structured_llm.invoke([HumanMessage(content=prompt)])
    except Exception:
        logger.exception("Router LLM call failed; falling back to chat intent.")
        decision = _safe_fallback_decision()

    decision = _normalize_decision(decision, previous_city)

    state["intent"] = decision.intent
    state["city"] = decision.city
    state["required_agents"] = decision.required_agents
    state["reasoning_trace"] = [
        *state.get("reasoning_trace", []),
        {
            "thought": decision.thought,
            "action": f"route_to:{','.join(decision.required_agents)}",
            "observation": f"intent={decision.intent}, city={decision.city or 'none'}",
        },
    ]

    if decision.city and decision.city != "Unknown":
        state["previous_city"] = decision.city
    return state

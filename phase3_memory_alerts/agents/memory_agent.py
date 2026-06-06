import json
import logging

from langchain_core.messages import HumanMessage

from graph.state import AgentState
from memory import database
from prompts.memory_prompt import MEMORY_PROMPT


logger = logging.getLogger(__name__)


def _parse_memory_action(query: str) -> dict:
    try:
        from agents.llm import llm

        prompt = f"{MEMORY_PROMPT}\n\nUser message: {query}"
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = json.loads(response.content)
        if parsed.get("memory_action") not in {"save_city", "get_city", "get_history", "none"}:
            return {"memory_action": "none", "city": ""}
        return parsed
    except Exception:
        logger.exception("Memory parser failed; defaulting to no memory action.")
        return {"memory_action": "none", "city": ""}


def run_memory(state: AgentState) -> AgentState:
    user_id = state.get("user_id") or "default_user"

    prefs = database.get_preference(user_id)
    state["memory_context"] = prefs
    if not state.get("city") and prefs.get("last_city"):
        state["city"] = prefs["last_city"]

    recent = database.get_recent_messages(user_id, limit=6)
    state["conversation_context"] = recent

    parsed = _parse_memory_action(state["user_query"])
    action = parsed.get("memory_action", "none")

    if action == "save_city":
        city = parsed.get("city", "").strip()
        database.save_preference(user_id, favorite_city=city, last_city=city)
        state["city"] = city
        state["final_response"] = (
            f"Got it! I've saved {city} as your favourite city. "
            f"I'll use it automatically for future questions."
        )
    elif action == "get_city":
        fav = prefs.get("favorite_city") or "not set yet"
        last = prefs.get("last_city") or "none"
        state["final_response"] = (
            f"Your saved favourite city is {fav}. "
            f"The last city you asked about was {last}."
        )
    elif action == "get_history":
        msgs = database.get_recent_messages(user_id, limit=5)
        if not msgs:
            state["final_response"] = "No conversation history yet."
        else:
            lines = [f"[{m['role'].upper()}] {m['content']}" for m in msgs]
            state["final_response"] = "Here's your recent conversation:\n" + "\n".join(lines)

    if state.get("city") and state["city"] != "Unknown":
        database.save_preference(user_id, last_city=state["city"])

    database.save_message(
        user_id,
        "user",
        state["user_query"],
        state.get("intent", ""),
        state.get("city", ""),
    )
    database.upsert_session(user_id)

    state["reasoning_trace"] = [
        *state.get("reasoning_trace", []),
        {
            "thought": "Processing memory-related request",
            "action": f"memory_action={parsed.get('memory_action', 'none')}",
            "observation": state.get("final_response", "")[:80],
        },
    ]
    return state

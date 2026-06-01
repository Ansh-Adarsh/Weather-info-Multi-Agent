import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from graph.state import AgentState
from prompts.conversation_prompt import CONVERSATION_PROMPT

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I'm your AI weather assistant. I can help with weather, forecasts, "
    "air quality, and outdoor recommendations."
)

MAX_HISTORY_MESSAGES = 10


def _build_chat_messages(state: AgentState) -> list:
    """Build a list of LangChain message objects from state for the LLM call.

    Includes the system prompt, recent conversation history, and the current
    user query.
    """
    messages: list = [SystemMessage(content=CONVERSATION_PROMPT)]

    # Include recent conversation history for context
    history = state.get("messages", [])[-MAX_HISTORY_MESSAGES:]
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    # Append the current user query
    messages.append(HumanMessage(content=state["user_query"]))
    return messages


def run_conversation(state: AgentState) -> AgentState:
    """LLM-powered conversational agent for chat-intent queries."""
    try:
        from agents.llm import llm

        chat_messages = _build_chat_messages(state)
        ai_response = llm.invoke(chat_messages)
        response = ai_response.content.strip()
    except Exception:
        logger.exception("Conversation LLM call failed; using fallback response.")
        response = FALLBACK_RESPONSE

    state["city"] = ""
    state["final_response"] = response
    state["messages"] = [
        *state.get("messages", []),
        {"role": "user", "content": state["user_query"]},
        {"role": "assistant", "content": response},
    ]
    return state

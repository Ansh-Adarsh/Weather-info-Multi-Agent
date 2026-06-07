import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path so we can import from graph and memory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from graph.workflow import app
from memory import database


def _scroll_chat_to_bottom() -> None:
    st.html(
        """
        <script>
        const scrollChat = () => {
            const root = window.parent.document.querySelector(
                ".st-key-chat_history"
            );
            if (!root) return;

            const candidates = [root, ...root.querySelectorAll("div")];
            const scroller = candidates.find(
                (element) => element.scrollHeight > element.clientHeight + 8
            );
            if (scroller) {
                scroller.scrollTop = scroller.scrollHeight;
            }
        };

        setTimeout(scrollChat, 80);
        setTimeout(scrollChat, 300);
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def _initial_state(user_input: str, user_id: str) -> dict:
    return {
        "user_query": user_input,
        "user_id": user_id,
        "intent": "",
        "city": "",
        "weather_data": {},
        "forecast_data": {},
        "aqi_data": {},
        "messages": [],
        "previous_city": st.session_state.get("last_city", ""),
        "reasoning_trace": [],
        "final_response": "",
        "memory_context": {},
        "conversation_context": [],
        "map_data": {},
    }


def render_chat(user_id: str) -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("prefill", "")
    st.session_state.setdefault("last_city", "")
    st.session_state.setdefault("map_data", {})

    if not st.session_state["messages"]:
        recent = database.get_recent_messages(user_id, limit=6)
        for msg in recent:
            st.session_state["messages"].append(
                {"role": msg["role"], "content": msg["content"]}
            )

    with st.container(key="chat_history", height=560, border=False):
        if not st.session_state["messages"]:
            st.caption("Start a conversation about weather, forecasts, or air quality.")

        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("meta"):
                    st.caption(
                        f"Intent: {msg['meta'].get('intent', '')} | "
                        f"City: {msg['meta'].get('city', '')}"
                    )

    _scroll_chat_to_bottom()

    with st.container(key="chat_composer"):
        user_input = st.session_state.pop("prefill", "") or st.chat_input(
            "Ask about weather anywhere...",
            key="weather_chat_input",
        )

    if user_input:
        user_msg = {"role": "user", "content": user_input}
        st.session_state["messages"].append(user_msg)

        with st.spinner("Thinking..."):
            result = app.invoke(_initial_state(user_input, user_id))

        st.session_state["last_city"] = result.get("city", "")
        st.session_state["map_data"] = result.get("map_data", {})
        assistant_msg = {
            "role": "assistant",
            "content": result["final_response"],
            "meta": {
                "intent": result.get("intent", ""),
                "city": result.get("city", ""),
            },
        }
        st.session_state["messages"].append(assistant_msg)

        st.rerun()

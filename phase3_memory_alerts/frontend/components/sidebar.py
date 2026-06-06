import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path so we can import from memory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memory import database


def render_sidebar() -> str:
    with st.sidebar:
        st.title("🌤 Weather Assistant")
        st.divider()

        st.subheader("User")
        user_id = st.text_input("User ID", value="default_user", key="user_id_input")
        st.caption("Your ID saves preferences across sessions.")

        st.subheader("Preferences")
        prefs = database.get_preference(user_id)
        col1, col2 = st.columns(2)
        col1.metric("Favourite city", prefs.get("favorite_city") or "Not set")
        col2.metric("Last city", prefs.get("last_city") or "None")

        st.subheader("Quick Actions")
        last_city = prefs.get("last_city", "your city") or "your city"
        if st.button("🌡 Current weather"):
            st.session_state["prefill"] = f"What is the weather in {last_city}?"
        if st.button("📅 7-day forecast"):
            st.session_state["prefill"] = f"What is the forecast for {last_city}?"
        if st.button("💨 Air quality"):
            st.session_state["prefill"] = f"What is the AQI in {last_city}?"

        st.subheader("Conversation")
        stats = database.get_session_stats(user_id)
        st.caption(f"Messages this session: {stats.get('message_count', 0)}")
        if st.button("🗑 Clear history"):
            database.clear_conversation(user_id)
            st.session_state["messages"] = []
            st.rerun()

        st.divider()
        st.caption("Powered by Groq + LangGraph")

    return user_id

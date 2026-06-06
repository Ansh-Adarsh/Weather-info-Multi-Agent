import streamlit as st

from components.chat import render_chat
from components.map_view import render_map
from components.sidebar import render_sidebar


st.set_page_config(
    page_title="AI Weather Assistant",
    page_icon="🌤",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #4A90D9;
        z-index: 9999;
    }
    [data-testid="stChatMessage"] {
        border-radius: 8px;
        padding: 0.35rem 0.5rem;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #EAF4FF;
        margin-left: 12%;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #FFFFFF;
        border: 1px solid #E6EAF0;
        margin-right: 12%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("💬 Chat")
    user_id = render_sidebar()
    render_chat(user_id)

with col2:
    st.subheader("🗺 City Map")
    map_data = st.session_state.get("map_data", {})
    render_map(map_data)

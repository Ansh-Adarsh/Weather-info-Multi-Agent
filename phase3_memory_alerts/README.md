# Phase 3 — Memory + ChatGPT UI + Map Visualization

## Overview
Full-stack conversational AI weather assistant extending Phase 2 with
persistent SQLite memory, a ChatGPT-style Streamlit chat UI, and a
Folium map that auto-updates with every query. No FastAPI needed —
Streamlit calls LangGraph directly for simplicity.

## What's New vs Phase 2
| Feature | What Changed |
| --- | --- |
| Phase 3.1 Memory | SQLite stores preferences, last city, full conversation history per user |
| Phase 3.2 UI | Two-column Streamlit layout: chat panel left, live map right, preference sidebar |
| Phase 3.3 Map | Folium map auto-centres on queried city, blue marker + coloured AQI circle overlay |
| save_response_node | New graph node that persists every response to DB and builds map_data before returning |

## Final Architecture
```text
  User
    ↓
  Streamlit UI  (chat + sidebar + map)
    ↓
  LangGraph Router  (Groq + Pydantic)
    ↓
  chat → Conversation Agent
  weather → Weather Agent
  forecast → Forecast Agent
  aqi → AQI Agent
  combined → Weather Agent → AQI Agent
  memory → Memory Agent
    ↓
  Recommendation Agent (Groq) or Memory Agent (direct)
    ↓
  save_response_node  (persist DB + build map_data)
    ↓
  SQLite Memory Layer    Folium Map
  (prefs + history)      (city pin + AQI circle)
    ↓
  Final response in Streamlit + map auto-updates
```

## Sub-Phase Breakdown
| Sub-Phase | What It Builds | Key New Files |
| --- | --- | --- |
| 3.1 Memory | SQLite DB + Memory Agent + DB-aware router | memory/database.py, agents/memory_agent.py, prompts/memory_prompt.py |
| 3.2 UI | Streamlit chat, sidebar quick actions, session state | frontend/app.py, components/chat.py, components/sidebar.py |
| 3.3 Map | Folium map + coordinate builder + AQI overlay | tools/map_utils.py, components/map_view.py |

## Agents
| Agent | Role | Uses Groq? | New in Phase 3? |
| --- | --- | --- | --- |
| Router | Intent + city + memory preload | Yes | Updated |
| Conversation | Chat + follow-ups | Yes | Phase 2 |
| Weather | Current conditions | No | Phase 2 |
| Forecast | 7-day forecast | No | Phase 2 |
| AQI | Air quality | No | Phase 2 |
| Memory Agent | Save prefs + history via LLM | Yes | New |
| Recommendation | Natural synthesis | Yes | Phase 2 |
| save_response_node | Persist + build map | No | New |

## Tech Stack
| Component | Technology |
| --- | --- |
| LLM | Groq (llama3-8b-8192) |
| Structured Output | Pydantic + with_structured_output |
| Agent Framework | LangGraph |
| Memory | SQLite (built-in Python) |
| UI Framework | Streamlit |
| Maps | Folium + streamlit-folium |
| Weather + Forecast | Open-Meteo (free) |
| Air Quality | OpenWeather (free tier) |

## Project Structure
```text
phase3_memory_alerts/
├── agents/
│   ├── __init__.py                 # Marks agents as a Python package
│   ├── llm.py                      # Phase 2 Groq ChatGroq client
│   ├── router.py                   # Updated router with memory intent + DB preload
│   ├── conversation_agent.py       # Phase 2 conversational chat agent
│   ├── weather_agent.py            # Phase 2 current weather agent
│   ├── forecast_agent.py           # Phase 2 7-day forecast agent
│   ├── aqi_agent.py                # Phase 2 air quality agent
│   ├── recommendation_agent.py     # Phase 2 recommendation synthesis agent
│   └── memory_agent.py             # Saves and retrieves preferences/history
├── tools/
│   ├── __init__.py                 # Marks tools as a Python package
│   ├── weather_api.py              # Phase 2 Open-Meteo weather API wrapper
│   ├── forecast_api.py             # Phase 2 Open-Meteo forecast API wrapper
│   ├── aqi_api.py                  # Phase 2 OpenWeather AQI API wrapper
│   └── map_utils.py                # Geocodes cities and builds map payloads
├── graph/
│   ├── __init__.py                 # Marks graph as a Python package
│   ├── state.py                    # Shared LangGraph state including memory/map fields
│   └── workflow.py                 # LangGraph workflow with memory and save node
├── prompts/
│   ├── __init__.py                 # Marks prompts as a Python package
│   ├── router_prompt.py            # Updated router prompt with memory intent
│   ├── conversation_prompt.py      # Phase 2 conversation prompt
│   ├── recommendation_prompt.py    # Phase 2 recommendation prompt
│   └── memory_prompt.py            # Memory action extraction prompt
├── memory/
│   ├── __init__.py                 # Marks memory as a Python package
│   └── database.py                 # SQLite tables and helper functions
├── frontend/
│   ├── app.py                      # Streamlit entry point
│   └── components/
│       ├── __init__.py             # Marks components as a Python package
│       ├── chat.py                 # Chat UI and LangGraph invocation
│       ├── sidebar.py              # User preferences and quick actions
│       └── map_view.py             # Folium map renderer
├── .env.example                    # Required API key template
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## Setup & Run
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GROQ_API_KEY and OPENWEATHER_API_KEY
streamlit run frontend/app.py
```

## UI Walkthrough
Left column — Chat:
ChatGPT-style conversation with intent + city caption
per response. Loads last 6 messages from DB on startup.

Right column — Map:
Folium map auto-centres on the last queried city.
Blue marker with popup showing temp, condition, AQI, rain %.
Coloured circle overlay: green=Good → darkred=Very Poor AQI.

Sidebar:
User ID input, favourite city and last city metrics,
one-click quick action buttons, message count, clear history.

## Example Session
```text
[Sidebar quick action: Current weather]
You: What is the weather in Mumbai?
[ Intent: weather | City: Mumbai ]
Assistant: Mumbai is warm and humid today at 31°C...
[Map centres on Mumbai, blue marker, green AQI circle]

You: My favourite city is Bangalore.
[ Intent: memory | City:  ]
Assistant: Got it! I've saved Bangalore as your favourite city.
[Sidebar preference updates: Favourite city → Bangalore]

You: What about air quality?
[ Intent: aqi | City: Bangalore ]
Assistant: Air quality in Bangalore is currently Moderate...
[Map updates to Bangalore, orange AQI circle]

You: Should I go for a run tomorrow morning?
[ Intent: combined | City: Bangalore ]
Assistant: Tomorrow morning in Bangalore looks clear at 24°C...
```

## Key Concepts
- Router always preloads memory context so city fallback
  works on every intent, not just memory intent
- save_response_node runs after every query ensuring
  history and map_data are always persisted before returning
- Folium map re-renders automatically because Streamlit
  re-runs the full script on each state change
- Sidebar quick actions write to st.session_state["prefill"]
  which chat.py reads on the next render pass
- SQLite DB is auto-created on first run, no setup needed

## Notes
- No FastAPI in Phase 3 — Streamlit calls LangGraph directly
- SQLite auto-created at memory/weather_memory.db on first run
- Swap llama3-8b-8192 for mixtral-8x7b-32768 in agents/llm.py
- Folium map needs internet to load CartoDB tile layer
- streamlit-folium must be installed separately (see requirements)

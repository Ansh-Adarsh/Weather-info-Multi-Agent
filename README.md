## There are two phase of this project 
1. phase-2 basic agent
2. Phase-3 streamlit based UI integrated agent

# 1. Phase 2 — Multi-Agent Weather System with Groq + LangGraph

## Overview
Intelligent multi-agent weather assistant powered by Groq LLM and LangGraph.
Uses ReAct-style reasoning, LLM-powered routing, and conversational responses
instead of static keyword matching and plain data output.

## What's in Phase 2

| Area               | Approach                                                 |
| ------------------ | -------------------------------------------------------- |
| Routing            | LLM-powered intent classification(Groq) + Pydantic structured output |
| Responses          | Conversational natural-language weather responses        |
| City Memory        | Maintains previous city context across follow-up queries |
| Prompt Engineering | Structured prompt templates plus validated router schema |
| Agent Logic        | ReAct-style reasoning with dynamic tool usage            |
| Workflow           | Multi-agent orchestration using LangGraph                |
| Recommendations    | Intelligent synthesis of weather, AQI, and forecast data |
| User Experience    | ChatGPT-like interactive weather assistant               |


## Architecture
```text
User Query
    |
    v
Router Agent (Groq LLM)
    |
    v
[Weather | Forecast | AQI | Combined]
    |
    v
Recommendation Agent (Groq LLM)
    |
    v
Conversational Response

Graph:-
User Query
   |
   v
Router Agent
(Groq + Pydantic structured output)
   |
   |-- intent = chat ---------> Conversation Agent ---------> Final Response
   |
   |-- intent = weather ------> Weather Agent --------------+
   |                                                        |
   |-- intent = forecast -----> Forecast Agent -------------+--> Recommendation Agent
   |                                                        |    (Groq structured synthesis)
   |-- intent = aqi ----------> AQI Agent ------------------+
   |
   |-- intent = combined -----> Weather Agent ----+
                              (parallel)          |
                                                  +----------> Recommendation Agent
                              AQI Agent ---------+             (final response)
                              
```
[Graph](image.png)

## Agents
| Agent | Role | Uses LLM? |
| --- | --- | --- |
| Router Agent | Intent detection + city extraction | Yes (Groq) |
| Weather Agent | Fetches current conditions | No |
| Forecast Agent | Fetches 7-day forecast | No |
| AQI Agent | Fetches air quality | No |
| Recommendation Agent | Synthesizes all data into natural response | Yes (Groq) |

## Tech Stack
| Component | Technology |
| --- | --- |
| LLM Provider | Groq (llama3-8b-8192) |
| Agent Framework | LangGraph |
| LLM Integration | LangChain + langchain-groq |
| Structured Output | Pydantic |
| Weather + Forecast | Open-Meteo (free) |
| Air Quality | OpenWeather API (free tier) |
| Language | Python 3.10+ |

## Project Structure
```text
phase2_multi_agent/
├── agents/
│   ├── __init__.py                 # Marks agents as a Python package
│   ├── llm.py                      # Initializes the Groq ChatGroq client
│   ├── router.py                   # Detects intent and city with keyword + LLM routing
│   ├── weather_agent.py            # Fetches current weather conditions
│   ├── forecast_agent.py           # Fetches the 7-day forecast
│   ├── aqi_agent.py                # Fetches air quality data
│   └── recommendation_agent.py     # Uses Groq to synthesize a conversational answer
├── tools/
│   ├── __init__.py                 # Marks tools as a Python package
│   ├── weather_api.py              # Calls Open-Meteo current weather endpoints
│   ├── forecast_api.py             # Calls Open-Meteo forecast endpoints
│   └── aqi_api.py                  # Calls OpenWeather air pollution endpoint
├── graph/
│   ├── __init__.py                 # Marks graph as a Python package
│   ├── state.py                    # Defines shared AgentState and memory fields
│   └── workflow.py                 # Builds and compiles the LangGraph workflow
├── prompts/
│   ├── __init__.py                 # Marks prompts as a Python package
│   ├── router_prompt.py            # Prompt template for LLM routing
│   └── recommendation_prompt.py    # Prompt template for conversational responses
├── main.py                         # Runs the interactive CLI with memory
├── .env.example                    # Documents required API keys
├── requirements.txt                # Lists Python dependencies
└── README.md                       # Project documentation
```

## Setup & Run
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Getting Free API Keys
- Groq: https://console.groq.com (free, fast inference)
- OpenWeather: https://openweathermap.org/api (free tier)

## Example Conversation
```text
You: What is the weather in Delhi?
[ Intent: weather | City: Delhi ]
Assistant: Delhi is experiencing quite hot conditions today at around 38°C,
with humidity making it feel closer to 42°C. The skies are partly cloudy,
which offers little relief from the heat. It's strongly recommended to
stay hydrated and avoid stepping out during peak afternoon hours if possible.

You: What about tomorrow?
[ Intent: forecast | City: Delhi ]
Assistant: Tomorrow in Delhi looks similar — temperatures expected between
35°C and 40°C with a 20% chance of light rain in the evening...
```

## Key Concepts
- Groq provides ultra-fast LLM inference for near-instant responses
- LLM-powered routing uses Pydantic structured output for validated intent and city extraction
- Conversation state (previous_city, messages) enables follow-up questions
- Two-stage LLM usage: routing + recommendation synthesis
- Fallback logic ensures the system works even if LLM calls fail

## Notes
- llama3-8b-8192 can be swapped for mixtral-8x7b-32768 in agents/llm.py
- Open-Meteo needs no API key — only OpenWeather AQI requires one
- All state resets per query except previous_city and messages


# 2. Phase 3 — Memory + ChatGPT UI + Map Visualization

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

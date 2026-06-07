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

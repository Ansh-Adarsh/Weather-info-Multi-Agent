from graph.workflow import app


def main() -> None:
    print("Multi-agent weather intelligence ready. Type exit, quit, or q to stop.")
    conversation_state = {
        "user_query": "",
        "intent": "",
        "city": "",
        "required_agents": [],
        "weather_data": {},
        "forecast_data": {},
        "aqi_data": {},
        "weather_summary": {},
        "aqi_summary": {},
        "messages": [],
        "previous_city": "",
        "reasoning_trace": [],
        "risk_level": "",
        "final_response": "",
    }

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        conversation_state["user_query"] = user_input
        conversation_state["weather_data"] = {}
        conversation_state["forecast_data"] = {}
        conversation_state["aqi_data"] = {}
        conversation_state["weather_summary"] = {}
        conversation_state["aqi_summary"] = {}
        conversation_state["required_agents"] = []
        conversation_state["reasoning_trace"] = []
        conversation_state["risk_level"] = ""
        conversation_state["final_response"] = ""

        try:
            result = app.invoke(conversation_state)
            conversation_state["previous_city"] = result["previous_city"]
            conversation_state["messages"] = result["messages"]

            print(f"\n[ Intent: {result['intent']} | City: {result['city']} ]")
            print(f"Assistant: {result['final_response']}\n")
        except Exception as exc:
            print(f"Assistant: Sorry, something went wrong while handling your request: {exc}")


if __name__ == "__main__":
    main()

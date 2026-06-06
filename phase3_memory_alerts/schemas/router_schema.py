from typing import Literal

from pydantic import BaseModel, Field


class RouterDecision(BaseModel):
    thought: str = Field(
        default="Route the user query to the best available graph node.",
        description="Brief reasoning about what the user needs."
    )
    intent: Literal["weather", "forecast", "aqi", "combined", "chat", "memory"] = Field(
        description="The high-level route for the query."
    )
    city: str = Field(
        default="",
        description="City extracted from the query, or empty when no city is needed."
    )
    required_agents: list[Literal["weather_agent", "forecast_agent", "aqi_agent", "conversation_agent", "memory_agent"]] = Field(
        default_factory=list,
        description="Graph agent nodes required to answer the query."
    )

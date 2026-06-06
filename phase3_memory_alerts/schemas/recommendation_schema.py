from typing import Literal

from pydantic import BaseModel, Field


class RecommendationOutput(BaseModel):
    summary: str = Field(description="Natural conversational weather summary.")
    advice: str = Field(description="One practical recommendation for the user.")
    risk_level: Literal["low", "moderate", "high", "unknown"] = Field(
        description="Overall outdoor/weather risk level."
    )


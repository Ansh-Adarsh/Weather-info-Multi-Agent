from pydantic import BaseModel, Field


class WeatherSummary(BaseModel):
    city: str
    temperature: float | None = None
    apparent_temperature: float | None = None
    humidity: int | None = None
    wind_speed: float | None = None
    condition: str = "unknown conditions"
    error: str | None = None


class AQISummary(BaseModel):
    city: str
    aqi_index: int | None = None
    aqi_label: str = "Unknown"
    pm2_5: float | None = Field(default=None, alias="pm2_5")
    pm10: float | None = None
    error: str | None = None


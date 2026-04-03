from pydantic import BaseModel, Field, field_validator

from app.constants.enums import DestinationType


class Preferences(BaseModel):
    safety_priority: int = Field(ge=1, le=10)
    cost_sensitivity: int = Field(ge=1, le=10)
    comfort_level: int = Field(ge=1, le=10)
    traffic_tolerance: int = Field(ge=1, le=10)
    pollution_tolerance: int = Field(ge=1, le=10)
    crowd_tolerance: int = Field(ge=1, le=10)


class AnalyzeRequest(BaseModel):
    city: str = Field(min_length=2, max_length=80)
    trip_duration_days: int = Field(ge=1, le=30)
    total_budget: float = Field(gt=0)
    start_location: str = Field(min_length=2, max_length=120)
    destination_type: DestinationType
    preferences: Preferences

    @field_validator("city", "start_location", mode="before")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(str(value).strip().split())

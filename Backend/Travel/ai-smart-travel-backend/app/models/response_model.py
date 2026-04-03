from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.constants.enums import BudgetFit, CrowdLevel, RouteType, SafetyLevel, TrafficLevel


class RecommendedArea(BaseModel):
    name: str
    safety_level: SafetyLevel
    crowd_level: CrowdLevel
    reason: str


class RouteOption(BaseModel):
    type: RouteType
    from_: str = Field(alias="from")
    to: str
    duration: str
    traffic_level: TrafficLevel

    model_config = ConfigDict(populate_by_name=True)


class StayOption(BaseModel):
    name: str
    price_per_night: int
    rating: float
    budget_fit: BudgetFit


class WeatherSnapshot(BaseModel):
    temperature_c: float
    condition: str


class DataSnapshot(BaseModel):
    weather: WeatherSnapshot
    aqi: int
    traffic_overall: TrafficLevel


class MetaInfo(BaseModel):
    response_time_ms: int
    data_sources: list[str]


class DebugInfo(BaseModel):
    raw_api_summaries: dict[str, dict[str, Any]]
    timings_ms: dict[str, int]


class AnalyzeResponse(BaseModel):
    travel_score: int
    city: str
    summary: str
    recommended_area: RecommendedArea
    routes: list[RouteOption]
    stay_options: list[StayOption]
    alerts: list[str]
    data_snapshot: DataSnapshot
    meta: MetaInfo
    debug: DebugInfo | None = None

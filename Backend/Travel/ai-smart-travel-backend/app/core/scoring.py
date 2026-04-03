from app.constants.enums import CrowdLevel, SafetyLevel, TrafficLevel
from app.core.utils import clamp
from app.models.request_model import AnalyzeRequest, Preferences


def build_preference_weights(preferences: Preferences) -> dict[str, float]:
    raw_weights = {
        "safety": preferences.safety_priority,
        "cost": preferences.cost_sensitivity,
        "comfort": preferences.comfort_level,
        "traffic": 11 - preferences.traffic_tolerance,
        "pollution": 11 - preferences.pollution_tolerance,
        "crowd": 11 - preferences.crowd_tolerance,
    }
    total = sum(raw_weights.values())
    return {key: value / total for key, value in raw_weights.items()}


def _safety_score(level: str) -> int:
    return {
        SafetyLevel.safe.value: 92,
        SafetyLevel.moderate.value: 68,
        SafetyLevel.risky.value: 35,
    }.get(level, 60)


def _traffic_score(level: str) -> int:
    return {
        TrafficLevel.low.value: 88,
        TrafficLevel.medium.value: 62,
        TrafficLevel.high.value: 34,
    }.get(level, 55)


def _crowd_score(level: str) -> int:
    return {
        CrowdLevel.low.value: 86,
        CrowdLevel.medium.value: 66,
        CrowdLevel.high.value: 44,
    }.get(level, 60)


def _pollution_score(aqi: int) -> int:
    if aqi <= 50:
        return 92
    if aqi <= 100:
        return 76
    if aqi <= 150:
        return 56
    if aqi <= 200:
        return 38
    return 24


def _cost_score(stay_options: list[dict], total_budget: float, trip_duration_days: int) -> int:
    if not stay_options:
        return 55
    average_price = sum(item["price_per_night"] for item in stay_options) / len(stay_options)
    required_budget = average_price * trip_duration_days
    coverage_ratio = total_budget / max(required_budget, 1)
    if coverage_ratio >= 1.3:
        return 92
    if coverage_ratio >= 1.0:
        return 78
    if coverage_ratio >= 0.85:
        return 58
    return 34


def _comfort_score(stay_options: list[dict], weather: dict) -> int:
    average_rating = 3.8
    if stay_options:
        average_rating = sum(item["rating"] for item in stay_options) / len(stay_options)
    score = average_rating * 20
    temperature = weather["temperature_c"]
    condition = weather["condition"].lower()
    if 20 <= temperature <= 29:
        score += 10
    elif temperature < 12 or temperature > 36:
        score -= 10
    if "haze" in condition or "storm" in condition:
        score -= 8
    elif "clear" in condition or "cloud" in condition:
        score += 4
    return int(clamp(round(score), 0, 100))


def build_factor_scores(
    request: AnalyzeRequest,
    recommended_area: dict,
    stay_options: list[dict],
    weather: dict,
    aqi: int,
    traffic_level: str,
) -> dict[str, int]:
    return {
        "safety": _safety_score(recommended_area["safety_level"]),
        "cost": _cost_score(stay_options, request.total_budget, request.trip_duration_days),
        "comfort": _comfort_score(stay_options, weather),
        "traffic": _traffic_score(traffic_level),
        "pollution": _pollution_score(aqi),
        "crowd": _crowd_score(recommended_area["crowd_level"]),
    }


def calculate_weighted_score(weights: dict[str, float], factor_scores: dict[str, int]) -> int:
    weighted_score = sum(weights[key] * factor_scores[key] for key in weights)
    return int(clamp(round(weighted_score), 0, 100))


def calculate_travel_score(
    request: AnalyzeRequest,
    recommended_area: dict,
    stay_options: list[dict],
    weather: dict,
    aqi: int,
    traffic_level: str,
) -> int:
    weights = build_preference_weights(request.preferences)
    factor_scores = build_factor_scores(
        request=request,
        recommended_area=recommended_area,
        stay_options=stay_options,
        weather=weather,
        aqi=aqi,
        traffic_level=traffic_level,
    )
    return calculate_weighted_score(weights, factor_scores)

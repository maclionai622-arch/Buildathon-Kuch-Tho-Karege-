import asyncio
import logging

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.core.scoring import build_factor_scores, build_preference_weights, calculate_weighted_score
from app.core.utils import (
    elapsed_ms,
    fit_budget,
    standard_error_payload,
    start_timer,
    structured_log,
)
from app.models.request_model import AnalyzeRequest
from app.models.response_model import AnalyzeResponse
from app.services.aqi_service import get_air_quality
from app.services.geocoding_service import InvalidLocationError, geocode_location
from app.services.places_service import get_stay_recommendations
from app.services.traffic_service import get_traffic_routes
from app.services.weather_service import get_weather

logger = logging.getLogger("ai_smart_travel.analyze")
router = APIRouter()


def _merge_alerts(*groups: list[str]) -> list[str]:
    """Merge multiple alert lists preserving order and removing duplicates."""
    ordered: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            if item and item not in seen:
                seen.add(item)
                ordered.append(item)
    return ordered


def _build_summary(
    city: str,
    score: int,
    recommended_area: dict,
    stay_options: list[dict],
    traffic_level: str,
    weather: dict,
    aqi: int,
) -> str:
    budget_fit = stay_options[0]["budget_fit"] if stay_options else "Moderate"
    return (
        f"{city} scores {score}/100 for this trip. "
        f"{recommended_area['name']} is the best match because it offers "
        f"{recommended_area['safety_level'].lower()} surroundings, "
        f"{recommended_area['crowd_level'].lower()} crowds, and {budget_fit.lower()} stay options. "
        f"Current conditions show {weather['condition'].lower()} weather, "
        f"overall {traffic_level.lower()} traffic, and AQI {aqi}."
    )


async def _timed_call(name: str, coroutine) -> tuple[str, object, int]:
    """Execute a coroutine and return (name, result_or_exception, elapsed_ms)."""
    started_at = start_timer()
    try:
        result = await coroutine
    except Exception as exc:
        return name, exc, elapsed_ms(started_at)
    return name, result, elapsed_ms(started_at)


# --- Route-level fallbacks (used when service itself throws an exception) ---

def _weather_fallback() -> dict:
    return {
        "temperature_c": 26.0,
        "condition": "Clear",
        "alerts": ["Some data may be outdated"],
        "debug_summary": {"provider": "route_fallback", "fallback_used": True, "cache_hit": False},
    }


def _aqi_fallback() -> dict:
    return {
        "aqi": 80,
        "alerts": ["Some data may be outdated"],
        "debug_summary": {"provider": "route_fallback", "fallback_used": True, "cache_hit": False},
    }


def _places_fallback(payload: AnalyzeRequest, city_geo: dict) -> dict:
    price_per_night = max(1200, round((payload.total_budget / max(payload.trip_duration_days, 1)) / 100) * 100)
    return {
        "stay_options": [
            {
                "name": f"{payload.city} Central Stay",
                "price_per_night": price_per_night,
                "rating": 3.8,
                "budget_fit": fit_budget(price_per_night, payload.total_budget, payload.trip_duration_days),
            }
        ],
        "recommended_area": {
            "name": f"{payload.city} Central",
            "safety_level": "Moderate",
            "crowd_level": "Medium",
            "reason": f"{payload.city} Central provides a balanced recommendation.",
        },
        "destination": {
            "name": f"{payload.city} Central",
            "lat": city_geo["lat"],
            "lng": city_geo["lng"],
        },
        "alerts": ["Some data may be outdated"],
        "debug_summary": {"provider": "route_fallback", "fallback_used": True, "cache_hit": False},
    }


def _traffic_fallback(payload: AnalyzeRequest, stay_data: dict) -> dict:
    return {
        "routes": [
            {
                "type": "fastest",
                "from": payload.start_location,
                "to": stay_data["destination"]["name"],
                "duration": "20 mins",
                "traffic_level": "Medium",
            },
            {
                "type": "safest",
                "from": payload.start_location,
                "to": stay_data["destination"]["name"],
                "duration": "25 mins",
                "traffic_level": "Low",
            },
        ],
        "overall": "Medium",
        "alerts": ["Some data may be outdated"],
        "debug_summary": {"provider": "route_fallback", "fallback_used": True, "cache_hit": False},
    }


@router.post("/analyze", response_model=AnalyzeResponse, response_model_exclude_none=True)
async def analyze_trip(payload: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    request_started_at = getattr(request.state, "request_started_at", start_timer())

    # Step 1: Geocode city and start location in parallel
    geocoding_results = await asyncio.gather(
        _timed_call("city_geocoding", geocode_location(payload.city)),
        _timed_call("start_geocoding", geocode_location(payload.start_location, city_context=payload.city)),
    )
    timings_ms = {name: timing for name, _, timing in geocoding_results}

    # Validate city geocoding result
    city_result = geocoding_results[0][1]
    if isinstance(city_result, InvalidLocationError):
        raise HTTPException(status_code=400, detail=standard_error_payload("Invalid location.", str(city_result)))
    if isinstance(city_result, Exception):
        raise HTTPException(
            status_code=500,
            detail=standard_error_payload("Geocoding failed.", str(city_result)),
        )

    city_geo = city_result
    alerts = list(city_geo.get("alerts", []))

    # Handle start location — fallback to city center if geocoding fails
    start_result = geocoding_results[1][1]
    if isinstance(start_result, Exception):
        start_geo = {
            "lat": city_geo["lat"],
            "lng": city_geo["lng"],
            "formatted_address": payload.start_location,
            "alerts": [],
            "debug_summary": {"provider": "route_fallback", "fallback_used": True, "cache_hit": False},
        }
        alerts = _merge_alerts(alerts, ["Start location could not be verified; using city center."])
    else:
        start_geo = start_result
        alerts = _merge_alerts(alerts, start_geo.get("alerts", []))

    # Step 2: Run weather, AQI, and places in parallel
    external_results = await asyncio.gather(
        _timed_call("weather", get_weather(city_geo["lat"], city_geo["lng"])),
        _timed_call("aqi", get_air_quality(city_geo["lat"], city_geo["lng"], payload.city)),
        _timed_call(
            "places",
            get_stay_recommendations(
                city=payload.city,
                lat=city_geo["lat"],
                lng=city_geo["lng"],
                total_budget=payload.total_budget,
                trip_duration_days=payload.trip_duration_days,
                destination_type=payload.destination_type.value,
            ),
        ),
    )
    timings_ms.update({name: timing for name, _, timing in external_results})

    weather_result = external_results[0][1]
    aqi_result = external_results[1][1]
    places_result = external_results[2][1]

    # Apply route-level fallbacks if any service threw an exception
    weather = weather_result if not isinstance(weather_result, Exception) else _weather_fallback()
    aqi_data = aqi_result if not isinstance(aqi_result, Exception) else _aqi_fallback()
    stay_data = places_result if not isinstance(places_result, Exception) else _places_fallback(payload, city_geo)

    # Step 3: Fetch traffic (depends on places destination)
    traffic_name, traffic_result, traffic_timing = await _timed_call(
        "traffic",
        get_traffic_routes(
            start_lat=start_geo["lat"],
            start_lng=start_geo["lng"],
            end_lat=stay_data["destination"]["lat"],
            end_lng=stay_data["destination"]["lng"],
            from_name=payload.start_location,
            to_name=stay_data["destination"]["name"],
        ),
    )
    timings_ms[traffic_name] = traffic_timing
    traffic_data = traffic_result if not isinstance(traffic_result, Exception) else _traffic_fallback(payload, stay_data)

    # Detect if any service used a route-level exception fallback
    any_route_fallback = (
        isinstance(weather_result, Exception)
        or isinstance(aqi_result, Exception)
        or isinstance(places_result, Exception)
        or isinstance(traffic_result, Exception)
    )
    fallback_alerts: list[str] = ["Some data may be outdated"] if any_route_fallback else []

    # Step 4: Merge all alerts
    alerts = _merge_alerts(
        alerts,
        weather["alerts"],
        aqi_data["alerts"],
        stay_data["alerts"],
        traffic_data["alerts"],
        fallback_alerts,
    )

    # Step 5: Compute weighted travel score
    weights = build_preference_weights(payload.preferences)
    factor_scores = build_factor_scores(
        request=payload,
        recommended_area=stay_data["recommended_area"],
        stay_options=stay_data["stay_options"],
        weather=weather,
        aqi=aqi_data["aqi"],
        traffic_level=traffic_data["overall"],
    )
    travel_score = calculate_weighted_score(weights, factor_scores)

    # Step 6: Build summary
    summary = _build_summary(
        city=payload.city,
        score=travel_score,
        recommended_area=stay_data["recommended_area"],
        stay_options=stay_data["stay_options"],
        traffic_level=traffic_data["overall"],
        weather=weather,
        aqi=aqi_data["aqi"],
    )

    response_time_ms = elapsed_ms(request_started_at)
    structured_log(
        logger,
        "info",
        "analysis_completed",
        city=payload.city,
        response_time_ms=response_time_ms,
        timings_ms=timings_ms,
    )

    # Debug payload — included when DEBUG_MODE is enabled
    debug_payload = None
    if settings.debug_mode:
        debug_payload = {
            "raw_api_summaries": {
                "geocoding": {
                    "city": city_geo.get("debug_summary", {}),
                    "start": start_geo.get("debug_summary", {}),
                },
                "weather": weather.get("debug_summary", {}),
                "aqi": aqi_data.get("debug_summary", {}),
                "places": stay_data.get("debug_summary", {}),
                "traffic": traffic_data.get("debug_summary", {}),
            },
            "timings_ms": timings_ms,
        }

    return AnalyzeResponse(
        travel_score=travel_score,
        city=payload.city,
        summary=summary,
        recommended_area=stay_data["recommended_area"],
        routes=traffic_data["routes"],
        stay_options=stay_data["stay_options"],
        alerts=alerts,
        data_snapshot={
            "weather": {
                "temperature_c": weather["temperature_c"],
                "condition": weather["condition"],
            },
            "aqi": aqi_data["aqi"],
            "traffic_overall": traffic_data["overall"],
        },
        meta={
            "response_time_ms": response_time_ms,
            "data_sources": ["weather", "traffic", "aqi", "places"],
        },
        debug=debug_payload,
    )

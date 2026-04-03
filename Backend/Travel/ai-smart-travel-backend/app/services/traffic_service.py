import logging

import httpx

from app.constants.enums import RouteType, TrafficLevel
from app.core.config import settings
from app.core.utils import build_cache_key, format_duration, get_cached_response

logger = logging.getLogger("ai_smart_travel.traffic")


def _traffic_level_from_ratio(ratio: float) -> str:
    """Classify traffic level based on duration_in_traffic / duration ratio."""
    if ratio <= 1.1:
        return TrafficLevel.low.value
    if ratio <= 1.3:
        return TrafficLevel.medium.value
    return TrafficLevel.high.value


def _downgrade_traffic_level(level: str) -> str:
    """Return one level lower traffic for the safest route."""
    if level == TrafficLevel.high.value:
        return TrafficLevel.medium.value
    return TrafficLevel.low.value


async def get_traffic_routes(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    from_name: str,
    to_name: str,
) -> dict:
    """Fetch real-time traffic and route data from Google Directions API."""
    cache_key = build_cache_key(
        "traffic",
        start_lat=start_lat,
        start_lng=start_lng,
        end_lat=end_lat,
        end_lng=end_lng,
        from_name=from_name,
        to_name=to_name,
    )

    async def fetch_traffic() -> dict:
        alerts: list[str] = []

        if settings.google_maps_api_key:
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(settings.request_timeout)) as client:
                    response = await client.get(
                        "https://maps.googleapis.com/maps/api/directions/json",
                        params={
                            "origin": f"{start_lat},{start_lng}",
                            "destination": f"{end_lat},{end_lng}",
                            "departure_time": "now",
                            "alternatives": "true",
                            "key": settings.google_maps_api_key,
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()

                    if payload.get("status") == "REQUEST_DENIED":
                        logger.warning("Directions API failed: REQUEST_DENIED. Please enable the 'Directions API' (not just Maps/Places) or switch to Routes API in Google Cloud.")
                    
                    if payload.get("status") == "OK" and payload.get("routes"):
                        parsed_routes = []
                        for route in payload["routes"]:
                            leg = route["legs"][0]
                            duration_seconds = int(leg["duration"]["value"])
                            # Use duration_in_traffic if available, else fall back to duration
                            traffic_duration = leg.get("duration_in_traffic", leg["duration"])
                            traffic_seconds = int(traffic_duration["value"])
                            traffic_ratio = traffic_seconds / max(duration_seconds, 1)

                            parsed_routes.append({
                                "duration_seconds": traffic_seconds,
                                "traffic_level": _traffic_level_from_ratio(traffic_ratio),
                                "traffic_ratio": traffic_ratio,
                            })

                        # Pick fastest (shortest duration) and safest (lowest traffic)
                        fastest = min(parsed_routes, key=lambda r: r["duration_seconds"])
                        safest = min(
                            parsed_routes,
                            key=lambda r: (
                                {"Low": 0, "Medium": 1, "High": 2}[r["traffic_level"]],
                                r["duration_seconds"],
                            ),
                        )

                        fastest_minutes = round(fastest["duration_seconds"] / 60)
                        routes = [
                            {
                                "type": RouteType.fastest.value,
                                "from": from_name,
                                "to": to_name,
                                "duration": format_duration(fastest_minutes),
                                "traffic_level": fastest["traffic_level"],
                            }
                        ]

                        if safest is fastest:
                            # Only one distinct route — synthesize safest with slightly longer duration
                            safest_minutes = round(fastest_minutes * 1.12)
                            routes.append({
                                "type": RouteType.safest.value,
                                "from": from_name,
                                "to": to_name,
                                "duration": format_duration(safest_minutes),
                                "traffic_level": _downgrade_traffic_level(fastest["traffic_level"]),
                            })
                        else:
                            safest_minutes = round(safest["duration_seconds"] / 60)
                            routes.append({
                                "type": RouteType.safest.value,
                                "from": from_name,
                                "to": to_name,
                                "duration": format_duration(safest_minutes),
                                "traffic_level": safest["traffic_level"],
                            })

                        overall = max(
                            (r["traffic_level"] for r in routes),
                            key=lambda level: {"Low": 0, "Medium": 1, "High": 2}[level],
                        )

                        # Generate alert for heavy traffic
                        if overall == TrafficLevel.high.value:
                            alerts.append("Heavy traffic expected")

                        logger.info("Traffic fetched: %s, overall=%s, %d route(s)",
                                    format_duration(fastest_minutes), overall, len(payload["routes"]))
                        return {
                            "routes": routes,
                            "overall": overall,
                            "alerts": alerts,
                            "debug_summary": {
                                "provider": "google_directions",
                                "fallback_used": False,
                                "route_count": len(routes),
                                "raw": {
                                    "google_routes_count": len(payload["routes"]),
                                    "fastest_minutes": fastest_minutes,
                                    "traffic_ratio": round(fastest.get("traffic_ratio", 1.0), 2),
                                },
                            },
                        }

            except Exception as exc:
                logger.warning("Traffic API call failed: %s", exc)

        # Fallback — only if API unavailable or failed
        return {
            "routes": [
                {
                    "type": RouteType.fastest.value,
                    "from": from_name,
                    "to": to_name,
                    "duration": "20 mins",
                    "traffic_level": TrafficLevel.medium.value,
                },
                {
                    "type": RouteType.safest.value,
                    "from": from_name,
                    "to": to_name,
                    "duration": "25 mins",
                    "traffic_level": TrafficLevel.low.value,
                },
            ],
            "overall": TrafficLevel.medium.value,
            "alerts": ["Some data may be outdated"],
            "debug_summary": {
                "provider": "fallback",
                "fallback_used": True,
            },
        }

    traffic_data, cache_hit = await get_cached_response(
        cache_key=cache_key,
        ttl_seconds=settings.cache_ttl_seconds,
        fetcher=fetch_traffic,
    )
    traffic_data["debug_summary"]["cache_hit"] = cache_hit
    return traffic_data

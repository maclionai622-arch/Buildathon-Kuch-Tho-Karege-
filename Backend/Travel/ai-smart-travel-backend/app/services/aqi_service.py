import logging

import httpx

from app.core.config import settings
from app.core.utils import build_cache_key, clamp, get_cached_response

logger = logging.getLogger("ai_smart_travel.aqi")

_OPENAQ_V3_URL = "https://api.openaq.org/v3/locations"


def _extract_aqi_from_v3_results(results: list[dict]) -> tuple[int | None, str | None, float | None, str | None]:
    """Parse OpenAQ v3 locations response for PM2.5 or PM10 data."""
    best_aqi: int | None = None
    best_param: str | None = None
    best_raw_value: float | None = None
    best_station: str | None = None

    for result in results:
        station_name = result.get("name", "Unknown")
        sensors = result.get("sensors", [])
        
        for sensor in sensors:
            param_info = sensor.get("parameter", {})
            param_name = param_info.get("name", "").lower()
            
            latest = sensor.get("latest", {})
            value = latest.get("value")
            
            if value is None:
                continue
                
            if param_name in ["pm25", "pm2.5"] and best_param not in ["pm25", "pm2.5"]:
                best_aqi = int(clamp(value, 0, 500))
                best_param = "pm25"
                best_raw_value = value
                best_station = station_name
            elif param_name == "pm10" and best_param not in ["pm25", "pm2.5"]:
                # Approximate PM2.5-equivalent from PM10
                best_aqi = int(clamp(value * 0.5, 0, 500))
                best_param = "pm10"
                best_raw_value = value
                best_station = station_name

    return best_aqi, best_param, best_raw_value, best_station


async def get_air_quality(lat: float, lng: float, city: str | None = None) -> dict:
    """Fetch air quality index from OpenAQ v3 API for the given coordinates."""
    cache_key = build_cache_key("aqi", lat=lat, lng=lng, city=city or "")

    async def fetch_air_quality() -> dict:
        headers: dict[str, str] = {}
        if settings.openaq_api_key:
            headers["X-API-Key"] = settings.openaq_api_key

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(settings.request_timeout)) as client:
                # --- TIER 1: Coordinate Search ---
                response = await client.get(
                    _OPENAQ_V3_URL,
                    headers=headers,
                    params={
                        "coordinates": f"{lat},{lng}",
                        "radius": 50000,
                        "limit": 3,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                results = payload.get("results", [])

                best_aqi, best_param, best_raw_value, best_station = _extract_aqi_from_v3_results(results)

                # --- TIER 2: City Fallback ---
                if best_aqi is None and city:
                    logger.info("No AQI data from coordinates, retrying with city='%s'", city)
                    city_response = await client.get(
                        _OPENAQ_V3_URL,
                        headers=headers,
                        params={
                            "city": city,
                            "limit": 3,
                        },
                    )
                    city_response.raise_for_status()
                    city_payload = city_response.json()
                    city_results = city_payload.get("results", [])

                    best_aqi, best_param, best_raw_value, best_station = _extract_aqi_from_v3_results(city_results)

                # --- Return real data if any attempt succeeded ---
                if best_aqi is not None:
                    alerts: list[str] = []
                    if best_aqi > 150:
                        alerts.append("High pollution detected")

                    logger.info("AQI fetched from OpenAQ v3: %d (%s)", best_aqi, best_param)
                    return {
                        "aqi": best_aqi,
                        "alerts": alerts,
                        "debug_summary": {
                            "provider": "openaq_v3",
                            "fallback_used": False,
                            "coordinates": {"lat": lat, "lng": lng},
                            "raw": {
                                best_param: best_raw_value,
                                "station": best_station,
                                "city": city,
                            },
                        },
                    }

        except Exception as exc:
            logger.warning("AQI API call failed (%s): %s", type(exc).__name__, exc)

        # --- TIER 3: Mock Fallback ---
        fallback_aqi = 80
        logger.info("Using AQI fallback value: %d", fallback_aqi)
        return {
            "aqi": fallback_aqi,
            "alerts": ["Some data may be outdated"],
            "debug_summary": {
                "provider": "fallback",
                "fallback_used": True,
                "coordinates": {"lat": lat, "lng": lng},
            },
        }

    aqi_data, cache_hit = await get_cached_response(
        cache_key=cache_key,
        ttl_seconds=settings.cache_ttl_seconds,
        fetcher=fetch_air_quality,
    )
    aqi_data["debug_summary"]["cache_hit"] = cache_hit
    return aqi_data

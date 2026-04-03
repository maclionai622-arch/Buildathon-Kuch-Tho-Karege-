import logging

import httpx

from app.core.config import settings
from app.core.utils import (
    build_cache_key,
    get_cached_response,
    normalize_temperature_celsius,
)

logger = logging.getLogger("ai_smart_travel.weather")

# Adverse weather conditions that trigger an alert
_ADVERSE_CONDITIONS = {"rain", "storm", "thunderstorm", "snow", "drizzle"}


async def get_weather(lat: float, lng: float) -> dict:
    """Fetch real-time weather from OpenWeatherMap for the given coordinates."""
    cache_key = build_cache_key("weather", lat=lat, lng=lng)

    async def fetch_weather() -> dict:
        # Always attempt real API call when key is available
        if settings.openweather_api_key:
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(settings.request_timeout)) as client:
                    response = await client.get(
                        "https://api.openweathermap.org/data/2.5/weather",
                        params={
                            "lat": lat,
                            "lon": lng,
                            "appid": settings.openweather_api_key,
                            "units": "metric",
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()

                    # Parse temperature and condition from real API response
                    temperature = normalize_temperature_celsius(
                        payload.get("main", {}).get("temp", 0)
                    )
                    condition = str(
                        payload.get("weather", [{}])[0].get("main", "Clear")
                    )

                    # Generate alert for adverse weather
                    alerts: list[str] = []
                    if condition.lower() in _ADVERSE_CONDITIONS:
                        alerts.append("Adverse weather conditions")

                    logger.info("Weather fetched from OpenWeatherMap: %.1f°C, %s", temperature, condition)
                    return {
                        "temperature_c": temperature,
                        "condition": condition,
                        "alerts": alerts,
                        "debug_summary": {
                            "provider": "openweathermap",
                            "fallback_used": False,
                            "coordinates": {"lat": lat, "lng": lng},
                            "raw": {
                                "temp": temperature,
                                "condition": condition,
                                "humidity": payload.get("main", {}).get("humidity"),
                                "wind_speed": payload.get("wind", {}).get("speed"),
                            },
                        },
                    }
            except Exception as exc:
                logger.warning("Weather API call failed (%s): %s", type(exc).__name__, exc)

        # Fallback — only reached if API key missing or API call failed
        return {
            "temperature_c": 26.0,
            "condition": "Clear",
            "alerts": ["Some data may be outdated"],
            "debug_summary": {
                "provider": "fallback",
                "fallback_used": True,
                "coordinates": {"lat": lat, "lng": lng},
            },
        }

    weather_data, cache_hit = await get_cached_response(
        cache_key=cache_key,
        ttl_seconds=settings.cache_ttl_seconds,
        fetcher=fetch_weather,
    )
    weather_data["debug_summary"]["cache_hit"] = cache_hit
    return weather_data

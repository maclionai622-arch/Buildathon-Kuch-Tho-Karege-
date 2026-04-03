import logging

import httpx

from app.core.config import settings
from app.core.utils import build_cache_key, get_cached_response

logger = logging.getLogger("ai_smart_travel.geocoding")


class InvalidLocationError(Exception):
    """Raised when a location cannot be resolved by any method."""
    pass


# Offline fallback for well-known locations — used ONLY when Google API is not available
KNOWN_LOCATIONS = {
    "delhi": {"lat": 28.6139, "lng": 77.2090, "formatted_address": "Delhi, India"},
    "new delhi": {"lat": 28.6139, "lng": 77.2090, "formatted_address": "New Delhi, India"},
    "new delhi railway station": {
        "lat": 28.6427, "lng": 77.2197,
        "formatted_address": "New Delhi Railway Station, Delhi, India",
    },
    "mumbai": {"lat": 19.0760, "lng": 72.8777, "formatted_address": "Mumbai, India"},
    "mumbai central station": {
        "lat": 18.9712, "lng": 72.8197,
        "formatted_address": "Mumbai Central Station, Mumbai, India",
    },
    "cst railway station": {
        "lat": 18.9402, "lng": 72.8356,
        "formatted_address": "Chhatrapati Shivaji Terminus, Mumbai, India",
    },
    "bengaluru": {"lat": 12.9716, "lng": 77.5946, "formatted_address": "Bengaluru, India"},
    "bangalore": {"lat": 12.9716, "lng": 77.5946, "formatted_address": "Bengaluru, India"},
    "jaipur": {"lat": 26.9124, "lng": 75.7873, "formatted_address": "Jaipur, India"},
    "kolkata": {"lat": 22.5726, "lng": 88.3639, "formatted_address": "Kolkata, India"},
    "chennai": {"lat": 13.0827, "lng": 80.2707, "formatted_address": "Chennai, India"},
    "hyderabad": {"lat": 17.3850, "lng": 78.4867, "formatted_address": "Hyderabad, India"},
    "pune": {"lat": 18.5204, "lng": 73.8567, "formatted_address": "Pune, India"},
    "ahmedabad": {"lat": 23.0225, "lng": 72.5714, "formatted_address": "Ahmedabad, India"},
    "goa": {"lat": 15.2993, "lng": 74.1240, "formatted_address": "Goa, India"},
    "leh": {"lat": 34.1526, "lng": 77.5771, "formatted_address": "Leh, Ladakh, India"},
    "manali": {"lat": 32.2396, "lng": 77.1887, "formatted_address": "Manali, Himachal Pradesh, India"},
    "shimla": {"lat": 31.1048, "lng": 77.1734, "formatted_address": "Shimla, Himachal Pradesh, India"},
    "udaipur": {"lat": 24.5854, "lng": 73.7125, "formatted_address": "Udaipur, Rajasthan, India"},
    "varanasi": {"lat": 25.3176, "lng": 83.0068, "formatted_address": "Varanasi, Uttar Pradesh, India"},
    "agra": {"lat": 27.1767, "lng": 78.0081, "formatted_address": "Agra, Uttar Pradesh, India"},
    "rishikesh": {"lat": 30.0869, "lng": 78.2676, "formatted_address": "Rishikesh, Uttarakhand, India"},
    "darjeeling": {"lat": 27.0360, "lng": 88.2627, "formatted_address": "Darjeeling, West Bengal, India"},
    "ooty": {"lat": 11.4102, "lng": 76.6950, "formatted_address": "Ooty, Tamil Nadu, India"},
    "amritsar": {"lat": 31.6340, "lng": 74.8723, "formatted_address": "Amritsar, Punjab, India"},
}


def _normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace(",", " ").split())


async def geocode_location(query: str, city_context: str | None = None) -> dict:
    """Convert a place name to lat/lng using Google Geocoding API with offline fallback."""
    cache_key = build_cache_key("geocode", query=query, city_context=city_context or "")

    async def fetch_geocode() -> dict:
        # Step 1: Try Google Geocoding API (real API call)
        if settings.google_maps_api_key:
            try:
                address = f"{query}, {city_context}" if city_context else query

                async with httpx.AsyncClient(timeout=httpx.Timeout(settings.request_timeout)) as client:
                    response = await client.get(
                        "https://maps.googleapis.com/maps/api/geocode/json",
                        params={
                            "address": address,
                            "key": settings.google_maps_api_key,
                        },
                    )
                    response.raise_for_status()
                    payload = response.json()

                    if payload.get("status") == "OK" and payload.get("results"):
                        result = payload["results"][0]
                        location = result["geometry"]["location"]
                        formatted_address = str(result.get("formatted_address", query))

                        logger.info("Geocoded '%s' → %s, %s (%s)",
                                    query, location["lat"], location["lng"], formatted_address)
                        return {
                            "lat": float(location["lat"]),
                            "lng": float(location["lng"]),
                            "formatted_address": formatted_address,
                            "alerts": [],
                            "debug_summary": {
                                "provider": "google_geocoding",
                                "fallback_used": False,
                                "query": query,
                                "raw": {
                                    "formatted_address": formatted_address,
                                    "location_type": result.get("geometry", {}).get("location_type"),
                                },
                            },
                        }

                    if payload.get("status") == "ZERO_RESULTS":
                        # No results from API for this query — check offline before raising
                        logger.warning("Google Geocoding returned ZERO_RESULTS for '%s'", query)
                    else:
                        # REQUEST_DENIED, OVER_QUERY_LIMIT, etc.
                        api_status = payload.get("status", "UNKNOWN")
                        error_msg = payload.get("error_message", "")
                        logger.warning("Google Geocoding returned %s for '%s': %s",
                                       api_status, query, error_msg)

            except Exception as exc:
                logger.warning("Geocoding API failed for '%s' (%s): %s", query, type(exc).__name__, exc)

        # Step 2: Offline fallback for known locations
        normalized = _normalize_key(query)
        if normalized in KNOWN_LOCATIONS:
            logger.info("Using offline lookup for '%s'", query)
            return {
                **KNOWN_LOCATIONS[normalized],
                "alerts": [],
                "debug_summary": {
                    "provider": "offline_lookup",
                    "fallback_used": True,
                    "query": query,
                },
            }

        # Step 3: Try city context if the exact query wasn't found
        if city_context:
            city_key = _normalize_key(city_context)
            if city_key in KNOWN_LOCATIONS:
                base = KNOWN_LOCATIONS[city_key]
                logger.info("Using city-context lookup for '%s' in '%s'", query, city_context)
                return {
                    "lat": base["lat"],
                    "lng": base["lng"],
                    "formatted_address": f"{query}, {base['formatted_address']}",
                    "alerts": [],
                    "debug_summary": {
                        "provider": "city_context_lookup",
                        "fallback_used": True,
                        "query": query,
                    },
                }

        # Nothing worked — this is truly an invalid location
        raise InvalidLocationError(f"Unable to resolve location '{query}'.")

    geocode_data, cache_hit = await get_cached_response(
        cache_key=cache_key,
        ttl_seconds=settings.cache_ttl_seconds,
        fetcher=fetch_geocode,
    )
    geocode_data["debug_summary"]["cache_hit"] = cache_hit
    return geocode_data

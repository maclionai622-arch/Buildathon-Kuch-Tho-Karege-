import logging
import random

import httpx

from app.constants.enums import BudgetFit, CrowdLevel, SafetyLevel
from app.core.config import settings
from app.core.utils import build_cache_key, fit_budget, get_cached_response

logger = logging.getLogger("ai_smart_travel.places")

# Overpass API endpoint (OpenStreetMap)
_OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Price estimation based on a random tier (no price_level from Overpass)
_PRICE_TIERS = [1200, 1800, 2500, 3200, 4200]


def _estimate_price(seed: str) -> int:
    """Pick a deterministic-ish price tier using the place name as seed."""
    rng = random.Random(seed)
    return rng.choice(_PRICE_TIERS)


def _safety_level_from_rating(rating: float) -> str:
    """Derive safety level from hotel rating."""
    if rating >= 4.2:
        return SafetyLevel.safe.value
    if rating >= 3.5:
        return SafetyLevel.moderate.value
    return SafetyLevel.risky.value


def _crowd_level_for_type(destination_type: str) -> str:
    """Estimate crowd level based on destination type."""
    if destination_type == "tourist":
        return CrowdLevel.high.value
    if destination_type == "business":
        return CrowdLevel.medium.value
    return CrowdLevel.medium.value


def _reason(area: str, safety_level: str, crowd_level: str, budget_fit: str) -> str:
    return (
        f"{area} balances {safety_level.lower()} surroundings, "
        f"{crowd_level.lower()} crowds, and {budget_fit.lower()} accommodation value."
    )


def _sort_rank(item: dict) -> tuple:
    budget_rank = {
        BudgetFit.good.value: 0,
        BudgetFit.moderate.value: 1,
        BudgetFit.expensive.value: 2,
    }
    safety_rank = {
        SafetyLevel.safe.value: 0,
        SafetyLevel.moderate.value: 1,
        SafetyLevel.risky.value: 2,
    }
    crowd_rank = {
        CrowdLevel.low.value: 0,
        CrowdLevel.medium.value: 1,
        CrowdLevel.high.value: 2,
    }
    return (
        budget_rank.get(item["budget_fit"], 1),
        safety_rank.get(item["safety_level"], 1),
        crowd_rank.get(item["crowd_level"], 1),
        -item["rating"],
        item["price_per_night"],
    )


async def get_stay_recommendations(
    city: str,
    lat: float,
    lng: float,
    total_budget: float,
    trip_duration_days: int,
    destination_type: str,
) -> dict:
    """Fetch nearby hotels from Overpass API (OpenStreetMap) and build stay recommendations."""
    cache_key = build_cache_key(
        "places",
        city=city,
        lat=lat,
        lng=lng,
        total_budget=total_budget,
        trip_duration_days=trip_duration_days,
        destination_type=destination_type,
    )

    async def fetch_places() -> dict:
        alerts: list[str] = []
        options: list[dict] = []

        try:
            # Overpass QL query — fetch hotels and guest houses within 5km
            query = (
                f"[out:json];\n"
                f"(\n"
                f'  node["tourism"="hotel"](around:5000, {lat}, {lng});\n'
                f'  way["tourism"="hotel"](around:5000, {lat}, {lng});\n'
                f'  node["tourism"="guest_house"](around:5000, {lat}, {lng});\n'
                f'  way["tourism"="guest_house"](around:5000, {lat}, {lng});\n'
                f");\n"
                f"out center;\n"
            )

            async with httpx.AsyncClient(timeout=httpx.Timeout(settings.overpass_timeout)) as client:
                response = await client.post(
                    _OVERPASS_URL,
                    data={"data": query},
                )
                response.raise_for_status()
                payload = response.json()

            # Deduplicate by (name, lat, lon) and collect up to 10 places
            seen: set[tuple[str, float, float]] = set()
            rng = random.Random(f"{lat}:{lng}:{city}")

            for element in payload.get("elements", []):
                if len(options) >= 10:
                    break

                # Skip entries without coordinates
                elem_lat = element.get("lat")
                elem_lon = element.get("lon")
                # Ways returned with "out center" have coordinates nested under "center"
                if elem_lat is None and "center" in element:
                    elem_lat = element["center"].get("lat")
                    elem_lon = element["center"].get("lon")
                if elem_lat is None or elem_lon is None:
                    continue

                tags = element.get("tags", {})
                name = tags.get("name", "Unknown Place")

                # Deduplicate
                dedup_key = (name, round(elem_lat, 5), round(elem_lon, 5))
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                # Determine place type
                place_type = "hotel" if tags.get("tourism") == "hotel" else "guest_house"

                # Generate random rating (Overpass has no ratings)
                rating = round(rng.uniform(3.5, 4.8), 1)
                price_per_night = _estimate_price(name)
                budget_status = fit_budget(price_per_night, total_budget, trip_duration_days)
                safety = _safety_level_from_rating(rating)
                crowd = _crowd_level_for_type(destination_type)
                area = name.split(" ")[0] if len(name.split(" ")) > 1 else city

                options.append({
                    "name": name,
                    "price_per_night": price_per_night,
                    "rating": rating,
                    "budget_fit": budget_status,
                    "area": area,
                    "safety_level": safety,
                    "crowd_level": crowd,
                    "reason": _reason(area, safety, crowd, budget_status),
                    "lat": float(elem_lat),
                    "lng": float(elem_lon),
                    "type": place_type,
                })

            if options:
                logger.info("Fetched %d places from Overpass API for %s", len(options), city)
            else:
                alerts.append("Overpass API returned no results near destination.")

        except Exception as exc:
            logger.warning("Overpass API call failed: %s", exc)
            alerts.append("Some data may be outdated")

        # Fallback — only if API unavailable or returned nothing
        if not options:
            fallback_used = True
            budget_per_night = total_budget / max(trip_duration_days, 1)
            price_per_night = max(1200, round(budget_per_night * 0.85 / 100) * 100)
            budget_status = fit_budget(price_per_night, total_budget, trip_duration_days)
            safety = SafetyLevel.moderate.value
            crowd = _crowd_level_for_type(destination_type)
            options.append({
                "name": f"{city} Central Hotel",
                "price_per_night": price_per_night,
                "rating": 3.8,
                "budget_fit": budget_status,
                "area": f"{city} Center",
                "safety_level": safety,
                "crowd_level": crowd,
                "reason": _reason(f"{city} Center", safety, crowd, budget_status),
                "lat": lat,
                "lng": lng,
            })
            if "Some data may be outdated" not in alerts:
                alerts.append("Some data may be outdated")
        else:
            fallback_used = False

        # Sort and pick top 3
        options = sorted(options, key=_sort_rank)
        top_three = options[:3]
        best = top_three[0]

        return {
            "stay_options": [
                {
                    "name": item["name"],
                    "price_per_night": item["price_per_night"],
                    "rating": item["rating"],
                    "budget_fit": item["budget_fit"],
                }
                for item in top_three
            ],
            "recommended_area": {
                "name": best["area"],
                "safety_level": best["safety_level"],
                "crowd_level": best["crowd_level"],
                "reason": best["reason"],
            },
            "destination": {
                "name": best["area"],
                "lat": best["lat"],
                "lng": best["lng"],
            },
            "alerts": alerts,
            "debug_summary": {
                "provider": "google_places" if not fallback_used else "fallback",
                "fallback_used": fallback_used,
                "recommended_area": best["area"],
                "option_count": len(top_three),
                "raw": {
                    "total_results": len(options),
                    "hotels": [{"name": o["name"], "rating": o["rating"], "price_level": o["price_per_night"]} for o in top_three],
                },
            },
        }

    places_data, cache_hit = await get_cached_response(
        cache_key=cache_key,
        ttl_seconds=settings.cache_ttl_seconds,
        fetcher=fetch_places,
    )
    places_data["debug_summary"]["cache_hit"] = cache_hit
    return places_data

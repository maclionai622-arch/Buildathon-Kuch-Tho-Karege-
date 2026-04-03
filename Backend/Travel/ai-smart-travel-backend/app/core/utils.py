import asyncio
import copy
import hashlib
import json
import logging
import math
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from app.constants.enums import BudgetFit

T = TypeVar("T")

_CACHE_STORE: dict[str, dict[str, Any]] = {}
_CACHE_LOCK = asyncio.Lock()


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_temperature_celsius(value: object) -> float:
    return round(safe_float(value, 0.0), 1)


def normalize_distance_km(value: object) -> float:
    return round(safe_float(value, 0.0), 2)


def format_duration(total_minutes: int) -> str:
    minutes = max(1, int(total_minutes))
    hours, remainder = divmod(minutes, 60)
    if hours == 0:
        return f"{remainder} mins"
    if remainder == 0:
        return f"{hours} hr"
    return f"{hours} hr {remainder} mins"


def fit_budget(price_per_night: float, total_budget: float, trip_duration_days: int) -> str:
    budget_per_night = total_budget / max(trip_duration_days, 1)
    if price_per_night <= budget_per_night * 0.9:
        return BudgetFit.good.value
    if price_per_night <= budget_per_night * 1.15:
        return BudgetFit.moderate.value
    return BudgetFit.expensive.value


def deterministic_float(seed: str, minimum: float, maximum: float) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    ratio = int(digest[:12], 16) / float(0xFFFFFFFFFFFF)
    return minimum + (maximum - minimum) * ratio


def deterministic_choice(seed: str, options: list[str]) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(options)
    return options[index]


def distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return normalize_distance_km(radius * c)


def start_timer() -> float:
    return time.perf_counter()


def elapsed_ms(start_time: float) -> int:
    return max(0, round((time.perf_counter() - start_time) * 1000))


def build_cache_key(prefix: str, **values: object) -> str:
    payload = json.dumps(values, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


async def get_cached_response(
    cache_key: str,
    ttl_seconds: int,
    fetcher: Callable[[], Awaitable[T]],
) -> tuple[T, bool]:
    now = time.monotonic()
    cached_entry = _CACHE_STORE.get(cache_key)
    if cached_entry and cached_entry["expires_at"] > now:
        return copy.deepcopy(cached_entry["value"]), True

    value = await fetcher()

    async with _CACHE_LOCK:
        _CACHE_STORE[cache_key] = {
            "expires_at": time.monotonic() + ttl_seconds,
            "value": copy.deepcopy(value),
        }

    return copy.deepcopy(value), False


def standard_error_payload(error: str, details: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"error": error}
    if details is not None:
        payload["details"] = details
    return payload


def configure_logging(level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def structured_log(logger: logging.Logger, level: str, event: str, **fields: object) -> None:
    message = json.dumps({"event": event, **fields}, default=str, ensure_ascii=False)
    getattr(logger, level.lower(), logger.info)(message)

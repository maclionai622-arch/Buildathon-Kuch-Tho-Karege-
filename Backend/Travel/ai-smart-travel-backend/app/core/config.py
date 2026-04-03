import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name: str = "AI Smart Travel Companion Backend"
    app_version: str = "1.0.0"
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    openaq_api_key: str = os.getenv("OPENAQ_API_KEY", "")
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "10"))
    overpass_timeout: float = float(os.getenv("OVERPASS_TIMEOUT", "25"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() in {"1", "true", "yes", "on"}
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

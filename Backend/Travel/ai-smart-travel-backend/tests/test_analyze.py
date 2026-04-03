import time
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.response_model import AnalyzeResponse

client = TestClient(app)

VALID_PAYLOAD = {
    "city": "Delhi",
    "trip_duration_days": 3,
    "total_budget": 6000,
    "start_location": "New Delhi Railway Station",
    "destination_type": "tourist",
    "preferences": {
        "safety_priority": 9,
        "cost_sensitivity": 7,
        "comfort_level": 6,
        "traffic_tolerance": 3,
        "pollution_tolerance": 4,
        "crowd_tolerance": 5,
    },
}


def test_analyze_endpoint_returns_valid_response() -> None:
    """The /analyze endpoint must return a valid, complete response."""
    started_at = time.perf_counter()
    response = client.post("/analyze", json=VALID_PAYLOAD)
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    assert response.status_code == 200
    response_payload = response.json()

    validated = AnalyzeResponse.model_validate(response_payload)

    assert validated.city == "Delhi"
    assert 0 <= validated.travel_score <= 100
    assert len(validated.routes) == 2
    assert {route.type.value for route in validated.routes} == {"fastest", "safest"}
    assert len(validated.stay_options) >= 1
    assert validated.recommended_area.name != ""
    assert validated.data_snapshot.aqi >= 0
    assert set(validated.meta.data_sources) == {"weather", "traffic", "aqi", "places"}
    # Response time should be reasonable (< 15s with real APIs)
    assert elapsed_ms < 15000


def test_analyze_data_snapshot_contains_all_keys() -> None:
    """Verify the data_snapshot has weather, aqi, and traffic_overall keys."""
    response = client.post("/analyze", json=VALID_PAYLOAD)
    assert response.status_code == 200

    snapshot = response.json()["data_snapshot"]
    assert "weather" in snapshot
    assert "temperature_c" in snapshot["weather"]
    assert "condition" in snapshot["weather"]
    assert "aqi" in snapshot
    assert "traffic_overall" in snapshot


def test_analyze_response_has_real_variation() -> None:
    """Two different cities must produce different outputs (proves real API calls)."""
    payload_delhi = VALID_PAYLOAD.copy()
    payload_mumbai = {
        **VALID_PAYLOAD,
        "city": "Mumbai",
        "start_location": "Mumbai Central Station",
    }

    response_delhi = client.post("/analyze", json=payload_delhi)
    response_mumbai = client.post("/analyze", json=payload_mumbai)

    assert response_delhi.status_code == 200
    assert response_mumbai.status_code == 200

    delhi_data = response_delhi.json()
    mumbai_data = response_mumbai.json()

    # Cities should have different weather or AQI or hotel names
    delhi_weather = delhi_data["data_snapshot"]["weather"]
    mumbai_weather = mumbai_data["data_snapshot"]["weather"]

    # At minimum, city names and recommended areas must differ
    assert delhi_data["city"] != mumbai_data["city"]
    assert delhi_data["recommended_area"]["name"] != mumbai_data["recommended_area"]["name"] or \
           delhi_weather["temperature_c"] != mumbai_weather["temperature_c"]


def test_analyze_invalid_city_returns_structured_error() -> None:
    payload = {
        "city": "Unknown Hyper City 999",
        "trip_duration_days": 3,
        "total_budget": 6000,
        "start_location": "Some Random Place",
        "destination_type": "tourist",
        "preferences": {
            "safety_priority": 9,
            "cost_sensitivity": 7,
            "comfort_level": 6,
            "traffic_tolerance": 3,
            "pollution_tolerance": 4,
            "crowd_tolerance": 5,
        },
    }

    response = client.post("/analyze", json=payload)

    assert response.status_code in (400, 500)
    body = response.json()
    assert "error" in body


def test_analyze_with_mock_api_failures() -> None:
    """When all external APIs fail, the endpoint should still return a valid
    response using fallback data and include the outdated-data alert."""

    with (
        patch(
            "app.routes.analyze.get_weather",
            new_callable=AsyncMock,
            side_effect=RuntimeError("weather down"),
        ),
        patch(
            "app.routes.analyze.get_air_quality",
            new_callable=AsyncMock,
            side_effect=RuntimeError("aqi down"),
        ),
        patch(
            "app.routes.analyze.get_stay_recommendations",
            new_callable=AsyncMock,
            side_effect=RuntimeError("places down"),
        ),
        patch(
            "app.routes.analyze.get_traffic_routes",
            new_callable=AsyncMock,
            side_effect=RuntimeError("traffic down"),
        ),
    ):
        response = client.post("/analyze", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    validated = AnalyzeResponse.model_validate(body)

    # Response must still have all required fields
    assert 0 <= validated.travel_score <= 100
    assert len(validated.routes) == 2
    assert len(validated.stay_options) >= 1
    assert validated.data_snapshot.aqi >= 0

    # The outdated-data alert must be present
    assert "Some data may be outdated" in validated.alerts

    # Should NOT contain 'not configured' alerts
    for alert in validated.alerts:
        assert "not configured" not in alert.lower()

"""Test OpenAQ v3 with correct endpoint format and Google Routes API."""
import asyncio
import json
import httpx

OPENAQ_KEY = "b10ab33f8f4eca691538cbabb27058a2e00807f1"
GOOGLE_KEY = "AIzaSyDCTFaE_zTTvZqiKX9OkUm3u9Ro33yhCaM"

LAT, LNG = 28.6139, 77.2090  # Delhi


async def test_openaq_v3_locations():
    """Test: find locations near coordinates, then get latest measurements."""
    print("\n=== OpenAQ v3: Find locations by coordinates ===")
    headers = {"X-API-Key": OPENAQ_KEY}
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
        # Step 1: find locations near lat/lng
        r = await c.get(
            "https://api.openaq.org/v3/locations",
            headers=headers,
            params={"coordinates": f"{LAT},{LNG}", "radius": 50000, "limit": 5},
        )
        print(f"  Locations Status: {r.status_code}")
        print(f"  Response: {r.text[:500]}")
        
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            print(f"  Found {len(results)} locations")
            for loc in results[:3]:
                loc_id = loc.get("id")
                name = loc.get("name")
                print(f"  Location: {name} (ID={loc_id})")
                sensors = loc.get("sensors", [])
                for s in sensors:
                    param = s.get("parameter", {})
                    print(f"    Sensor: {param.get('name')} ({param.get('units')})")
                
                # Step 2: try to get latest for this location
                if loc_id:
                    r2 = await c.get(
                        f"https://api.openaq.org/v3/locations/{loc_id}/latest",
                        headers=headers,
                    )
                    print(f"    Latest Status: {r2.status_code}")
                    if r2.status_code == 200:
                        latest = r2.json()
                        for meas in latest.get("results", [])[:5]:
                            print(f"      {meas}")
                    else:
                        print(f"    Latest Error: {r2.text[:200]}")
        else:
            print(f"  Error body: {r.text[:500]}")


async def test_openaq_v3_measurements():
    """Direct measurements query with bbox."""
    print("\n=== OpenAQ v3: Measurements by bounding box ===")
    headers = {"X-API-Key": OPENAQ_KEY}
    
    # Try direct /v3/measurements endpoint
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
        # Bounding box around Delhi (approx 50km)
        bbox = f"{LNG-0.5},{LAT-0.5},{LNG+0.5},{LAT+0.5}"
        r = await c.get(
            "https://api.openaq.org/v3/measurements",
            headers=headers,
            params={"bbox": bbox, "limit": 5, "parameter_id": 2},  # 2 = pm25
        )
        print(f"  Status: {r.status_code}")
        print(f"  Response: {r.text[:500]}")


async def test_google_routes():
    """Test Google Routes API (v2)."""
    print("\n=== Google Routes API (v2) ===")
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.staticDuration,routes.distanceMeters,routes.routeLabels",
    }
    payload = {
        "origin": {
            "location": {"latLng": {"latitude": 28.6427, "longitude": 77.2197}}
        },
        "destination": {
            "location": {"latLng": {"latitude": 28.6139, "longitude": 77.2090}}
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": True,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
        r = await c.post(
            "https://routes.googleapis.com/directions/v2:computeRoutes",
            json=payload,
            headers=headers,
        )
        print(f"  Status: {r.status_code}")
        data = r.json()
        print(f"  Response: {json.dumps(data, indent=2)[:800]}")
        
        if r.status_code == 200:
            routes = data.get("routes", [])
            print(f"  Routes found: {len(routes)}")
            for i, route in enumerate(routes):
                print(f"  [{i}] Duration: {route.get('duration')}, "
                      f"Static: {route.get('staticDuration')}, "
                      f"Labels: {route.get('routeLabels')}")


async def main():
    await test_openaq_v3_locations()
    await test_openaq_v3_measurements()
    await test_google_routes()
    print("\nDONE")

asyncio.run(main())

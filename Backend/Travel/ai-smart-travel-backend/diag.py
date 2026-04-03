import asyncio
import json
import httpx
from app.core.config import settings

LAT, LNG = 28.6139, 77.2090  # Delhi

async def test_openaq_v3_locations():
    print("\n=== OpenAQ v3: Find locations ===")
    headers = {"X-API-Key": settings.openaq_api_key}
    print(f"Using Key: {settings.openaq_api_key[:5]}...")
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.get(
            "https://api.openaq.org/v3/locations",
            headers=headers,
            params={"coordinates": f"{LAT},{LNG}", "radius": 50000, "limit": 3},
        )
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Body: {r.text}")
        else:
            data = r.json()
            for loc in data.get("results", [])[:2]:
                print(f" Location {loc.get('id')}: {loc.get('name')}")

async def test_google_directions():
    print("\n=== Google Directions ===")
    print(f"Using Key: {settings.google_maps_api_key[:10]}...")
    async with httpx.AsyncClient(timeout=15.0) as c:
        r = await c.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params={
                "origin": "28.6427,77.2197",
                "destination": "28.6139,77.2090",
                "departure_time": "now",
                "alternatives": "true",
                "key": settings.google_maps_api_key,
            },
        )
        print(f"Status HTTP: {r.status_code}")
        data = r.json()
        print(f"API Status: {data.get('status')}")
        if data.get('status') != "OK":
            print(f"Error: {data.get('error_message')}")

async def main():
    await test_openaq_v3_locations()
    await test_google_directions()

if __name__ == "__main__":
    asyncio.run(main())

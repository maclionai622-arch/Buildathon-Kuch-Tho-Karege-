"""Quick diagnostic: test each external API independently."""
import asyncio
import time
import httpx

OPENWEATHER_KEY = "f58d75e41beb3a82dd47855667dab11f"
GOOGLE_KEY = "AIzaSyDCTFaE_zTTvZqiKX9OkUm3u9Ro33yhCaM"
OPENAQ_KEY = "b10ab33f8f4eca691538cbabb27058a2e00807f1"

LAT, LNG = 28.6139, 77.2090  # Delhi


async def test_openweather():
    print("\n=== OpenWeatherMap ===")
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
            r = await c.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"lat": LAT, "lon": LNG, "appid": OPENWEATHER_KEY, "units": "metric"},
            )
            elapsed = round((time.perf_counter() - t0) * 1000)
            print(f"  Status: {r.status_code}  ({elapsed}ms)")
            data = r.json()
            if r.status_code == 200:
                print(f"  Temp: {data['main']['temp']}°C, Condition: {data['weather'][0]['main']}")
            else:
                print(f"  Error: {data}")
    except Exception as e:
        elapsed = round((time.perf_counter() - t0) * 1000)
        print(f"  EXCEPTION ({elapsed}ms): {type(e).__name__}: {e}")


async def test_openaq():
    print("\n=== OpenAQ v2 ===")
    t0 = time.perf_counter()
    try:
        headers = {"X-API-Key": OPENAQ_KEY}
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
            r = await c.get(
                "https://api.openaq.org/v2/latest",
                headers=headers,
                params={"coordinates": f"{LAT},{LNG}", "radius": 50000, "limit": 5},
            )
            elapsed = round((time.perf_counter() - t0) * 1000)
            print(f"  Status: {r.status_code}  ({elapsed}ms)")
            data = r.json()
            results = data.get("results", [])
            print(f"  Results count: {len(results)}")
            if results:
                for i, res in enumerate(results[:3]):
                    meas = res.get("measurements", [])
                    params = [(m.get("parameter"), m.get("value")) for m in meas]
                    print(f"  [{i}] {res.get('location', '?')} -> {params}")
            else:
                print(f"  Full response: {data}")
    except Exception as e:
        elapsed = round((time.perf_counter() - t0) * 1000)
        print(f"  EXCEPTION ({elapsed}ms): {type(e).__name__}: {e}")


async def test_openaq_v3():
    """Test OpenAQ v3 endpoint in case v2 is deprecated."""
    print("\n=== OpenAQ v3 (alternate) ===")
    t0 = time.perf_counter()
    try:
        headers = {"X-API-Key": OPENAQ_KEY}
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
            r = await c.get(
                "https://api.openaq.org/v3/locations",
                headers=headers,
                params={"coordinates": f"{LAT},{LNG}", "radius": 50000, "limit": 5},
            )
            elapsed = round((time.perf_counter() - t0) * 1000)
            print(f"  Status: {r.status_code}  ({elapsed}ms)")
            data = r.json()
            print(f"  Keys: {list(data.keys())}")
            results = data.get("results", [])
            print(f"  Results count: {len(results)}")
            if results:
                for i, res in enumerate(results[:2]):
                    print(f"  [{i}] {res.get('name', '?')} -> sensors: {[s.get('parameter',{}).get('name','?') for s in res.get('sensors',[])]}")
    except Exception as e:
        elapsed = round((time.perf_counter() - t0) * 1000)
        print(f"  EXCEPTION ({elapsed}ms): {type(e).__name__}: {e}")


async def test_google_directions():
    print("\n=== Google Directions ===")
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
            r = await c.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                params={
                    "origin": "28.6427,77.2197",
                    "destination": "28.6139,77.2090",
                    "departure_time": "now",
                    "alternatives": "true",
                    "key": GOOGLE_KEY,
                },
            )
            elapsed = round((time.perf_counter() - t0) * 1000)
            print(f"  Status HTTP: {r.status_code}  ({elapsed}ms)")
            data = r.json()
            api_status = data.get("status")
            print(f"  API Status: {api_status}")
            if api_status != "OK":
                print(f"  Error message: {data.get('error_message', 'N/A')}")
            else:
                routes = data.get("routes", [])
                print(f"  Routes: {len(routes)}")
                for i, route in enumerate(routes):
                    leg = route["legs"][0]
                    print(f"  [{i}] Duration: {leg['duration']['text']}, "
                          f"Traffic: {leg.get('duration_in_traffic', {}).get('text', 'N/A')}")
    except Exception as e:
        elapsed = round((time.perf_counter() - t0) * 1000)
        print(f"  EXCEPTION ({elapsed}ms): {type(e).__name__}: {e}")


async def test_overpass():
    print("\n=== Overpass (OpenStreetMap) ===")
    query = (
        f"[out:json];\n"
        f"(\n"
        f'  node["tourism"="hotel"](around:5000, {LAT}, {LNG});\n'
        f'  way["tourism"="hotel"](around:5000, {LAT}, {LNG});\n'
        f'  node["tourism"="guest_house"](around:5000, {LAT}, {LNG});\n'
        f'  way["tourism"="guest_house"](around:5000, {LAT}, {LNG});\n'
        f");\n"
        f"out center;\n"
    )
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as c:
            r = await c.post(
                "https://overpass-api.de/api/interpreter",
                data={"data": query},
            )
            elapsed = round((time.perf_counter() - t0) * 1000)
            print(f"  Status: {r.status_code}  ({elapsed}ms)")
            data = r.json()
            elements = data.get("elements", [])
            print(f"  Elements: {len(elements)}")
            named = [e for e in elements if e.get("tags", {}).get("name")]
            print(f"  Named places: {len(named)}")
            for e in named[:5]:
                print(f"    - {e['tags']['name']}")
    except Exception as e:
        elapsed = round((time.perf_counter() - t0) * 1000)
        print(f"  EXCEPTION ({elapsed}ms): {type(e).__name__}: {e}")


async def main():
    print("=" * 60)
    print("API DIAGNOSTIC TEST")
    print("=" * 60)
    await test_openweather()
    await test_openaq()
    await test_openaq_v3()
    await test_google_directions()
    await test_overpass()
    print("\n" + "=" * 60)
    print("DONE")

asyncio.run(main())

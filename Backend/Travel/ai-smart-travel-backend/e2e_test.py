import asyncio
import json
import httpx

async def test_e2e():
    print("=== E2E Test /analyze endpoint ===")
    url = "http://localhost:8001/analyze"
    payload = {
        "city": "Delhi",
        "start_location": "New Delhi Railway Station",
        "total_budget": 50000,
        "trip_duration_days": 4,
        "destination_type": "tourist",
        "preferences": {
            "safety_priority": 8,
            "cost_sensitivity": 5,
            "comfort_level": 7,
            "traffic_tolerance": 4,
            "pollution_tolerance": 3,
            "crowd_tolerance": 6
        }
    }
    
    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            r = await client.post(url, json=payload)
            print(f"Status: {r.status_code}")
            
            data = r.json()
            
            # Print the summary
            print("\n--- Summary ---")
            print(data.get("summary", "No summary"))
            
            # Print APIs health from debug
            if "debug" in data and data["debug"]:
                summaries = data["debug"].get("raw_api_summaries", {})
                
                print("\n--- API Health ---")
                weather = summaries.get("weather", {})
                print(f"Weather: {'Mocking' if weather.get('fallback_used') else 'Live'} (Provider: {weather.get('provider')})")
                
                aqi = summaries.get("aqi", {})
                print(f"AQI: {'Mocking' if aqi.get('fallback_used') else 'Live'} (Provider: {aqi.get('provider')})")
                
                places = summaries.get("places", {})
                print(f"Places: {'Mocking' if places.get('fallback_used') else 'Live'} (Provider: {places.get('provider')})")
                
                traffic = summaries.get("traffic", {})
                print(f"Traffic: {'Mocking' if traffic.get('fallback_used') else 'Live'} (Provider: {traffic.get('provider')})")
                print(f"\nResponse Time: {data['meta']['response_time_ms']} ms")
            else:
                print("\n--- Route Outputs ---")
                print(f"Weather: {data.get('data_snapshot', {}).get('weather')}")
                print(f"AQI: {data.get('data_snapshot', {}).get('aqi')}")
                print(f"Traffic Overall: {data.get('data_snapshot', {}).get('traffic_overall')}")
                print(f"\nResponse Time: {data.get('meta', {}).get('response_time_ms')} ms")
                
            print("\nRaw Output:")
            print(json.dumps(data, indent=2)[:1000])
                
        except Exception as e:
            print(f"E2E Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_e2e())

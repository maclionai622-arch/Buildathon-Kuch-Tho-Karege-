# AI Smart Travel Companion Backend

Production-ready FastAPI backend for analyzing city travel conditions and returning structured recommendations for frontend integration.

## Tech Stack

- Python 3.10+
- FastAPI
- httpx
- Pydantic
- python-dotenv
- pytest

## Project Structure

```text
ai-smart-travel-backend/
├── app/
│   ├── main.py
│   ├── routes/
│   │   └── analyze.py
│   ├── services/
│   │   ├── weather_service.py
│   │   ├── traffic_service.py
│   │   ├── aqi_service.py
│   │   ├── places_service.py
│   │   └── geocoding_service.py
│   ├── core/
│   │   ├── config.py
│   │   ├── scoring.py
│   │   └── utils.py
│   ├── models/
│   │   ├── request_model.py
│   │   └── response_model.py
│   └── constants/
│       └── enums.py
├── tests/
│   └── test_analyze.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment on Windows

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the environment file

```bash
copy .env.example .env
```

Optional environment variables:

- WEATHER_API_KEY
- GOOGLE_MAPS_API_KEY
- AQI_API_KEY
- REQUEST_TIMEOUT
- CACHE_TTL_SECONDS
- DEBUG_MODE
- LOG_LEVEL

The backend still works without live keys by using normalized fallback data and alert messages.

## Run the server

```bash
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```

## Run Postman

- Import [AI Smart Travel Companion.postman_collection.json](file:///c:/Users/Utkarsh/Documents/Karke/Backend/Travel/ai-smart-travel-backend/postman/AI%20Smart%20Travel%20Companion.postman_collection.json)
- Import [AI Smart Travel Companion.local.postman_environment.json](file:///c:/Users/Utkarsh/Documents/Karke/Backend/Travel/ai-smart-travel-backend/postman/AI%20Smart%20Travel%20Companion.local.postman_environment.json)
- Select the `AI Smart Travel Companion Local` environment
- Use the included requests for:
  - `GET /health`
  - `POST /analyze` valid request
  - `POST /analyze` low-budget edge case
  - `POST /analyze` invalid location
- The collection includes pre-request logging for request timestamp and request payload
- The collection also includes response validation tests for success and error scenarios

## API Endpoint

### POST /analyze

### Example request

```json
{
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
    "crowd_tolerance": 5
  }
}
```

### Example response

```json
{
  "travel_score": 72,
  "city": "Delhi",
  "summary": "Delhi scores 72/100 for this trip. Connaught Place is the best match because it offers safe surroundings, medium crowds, and good stay options. Current conditions show clear weather, overall medium traffic, and AQI 113.",
  "recommended_area": {
    "name": "Connaught Place",
    "safety_level": "Safe",
    "crowd_level": "Medium",
    "reason": "Connaught Place balances safe surroundings, medium crowds, and good accommodation value."
  },
  "routes": [
    {
      "type": "fastest",
      "from": "New Delhi Railway Station",
      "to": "Connaught Place",
      "duration": "18 mins",
      "traffic_level": "Medium"
    },
    {
      "type": "safest",
      "from": "New Delhi Railway Station",
      "to": "Connaught Place",
      "duration": "20 mins",
      "traffic_level": "Low"
    }
  ],
  "stay_options": [
    {
      "name": "Connaught Place Suites",
      "price_per_night": 1400,
      "rating": 4.5,
      "budget_fit": "Good"
    },
    {
      "name": "Karol Bagh Residency",
      "price_per_night": 1800,
      "rating": 4.2,
      "budget_fit": "Good"
    },
    {
      "name": "South Delhi Inn",
      "price_per_night": 2200,
      "rating": 4.0,
      "budget_fit": "Expensive"
    }
  ],
  "alerts": [
    "Using offline geocoding fallback.",
    "Weather API not configured; using fallback weather conditions.",
    "AQI API not configured; using fallback air quality data.",
    "Google Maps API not configured; using fallback stay options.",
    "Google Maps API not configured; using fallback route estimates."
  ],
  "data_snapshot": {
    "weather": {
      "temperature_c": 27.4,
      "condition": "Clear"
    },
    "aqi": 113,
    "traffic_overall": "Medium"
  },
  "meta": {
    "response_time_ms": 148,
    "data_sources": ["weather", "traffic", "aqi", "places"]
  }
}
```

## How to test /analyze

- Start the server with `uvicorn app.main:app --reload`
- Open Postman and use the collection in the `postman` folder
- Run `Analyze Trip` for a standard validation pass
- Run `Analyze Trip Low Budget` to verify edge-case scoring behavior
- Run `Analyze Trip Invalid Location` to verify standardized error handling

## Expected response format

- `travel_score`: integer score from 0 to 100
- `summary`: human-readable recommendation summary
- `recommended_area`: structured best-fit area recommendation
- `routes`: normalized fastest and safest route options
- `stay_options`: normalized accommodation recommendations
- `alerts`: fallback and API warning messages
- `data_snapshot`: current weather, AQI, and traffic overview
- `meta.response_time_ms`: total backend response time in milliseconds
- `meta.data_sources`: normalized source labels used by the response
- `debug`: optional debug-only payload with per-service timings and summarized provider output when `DEBUG_MODE=true`

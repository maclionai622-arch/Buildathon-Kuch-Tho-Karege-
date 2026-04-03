import type { AnalyzeRequest, AnalyzeResponse, RouteOption, StayOption, Alert, DataSnapshot } from "../types/api";

type DemoDataMap = Record<string, AnalyzeResponse>;

export const demoDataMap: DemoDataMap = {
  Delhi: {
    travel_score: 74,
    city: "Delhi",
    start_coordinates: [28.6139, 77.2090],
    summary: "Historic significance meets bustling crowds. High pollution expected; indoor/filtered transport recommended.",
    recommended_area: {
      name: "Connaught Place",
      safety_rating: 8,
      accessibility: "High"
    },
    routes: [
      { id: "del-r1", type: "Fastest", time: "45 mins", risk_level: "Moderate", traffic_level: "High", description: "Main arterial roads; expect heavy congestion.", destination_coordinates: [28.6339, 77.2190] },
      { id: "del-r2", type: "Safest", time: "55 mins", risk_level: "Safe", traffic_level: "Medium", description: "Use Metro infrastructure to bypass surface traffic.", destination_coordinates: [28.6139, 77.2290] }
    ],
    stay_options: [
      { id: "del-s1", name: "Imperial Suite", rating: 4.8, price: 15000, summary: "Luxury heritage stay.", coordinates: [28.6139, 77.2150] },
      { id: "del-s2", name: "CP Pods", rating: 4.1, price: 2000, summary: "Modern budget pods.", coordinates: [28.6329, 77.2195] }
    ],
    alerts: [{ id: "del-a1", type: "warning", message: "Severe AQI detected. N95 equivalent masks recommended." }],
    data_snapshot: { temperature: "32°C", aqi: 350, traffic_level: "High", overall_rating: 7.4 }
  },
  Mumbai: {
    travel_score: 85,
    city: "Mumbai",
    start_coordinates: [19.0760, 72.8777],
    summary: "The financial capital. Expect high humidity and medium traffic.",
    recommended_area: { name: "Bandra West", safety_rating: 9, accessibility: "High" },
    routes: [
      { id: "mum-r1", type: "Recommended", time: "30 mins", risk_level: "Safe", traffic_level: "Medium", description: "Sea Link reduces travel time significantly.", destination_coordinates: [19.0522, 72.8258] }
    ],
    stay_options: [
      { id: "mum-s1", name: "Taj Lands End", rating: 4.9, price: 22000, summary: "Premium luxury with sea views.", coordinates: [19.0436, 72.8193] }
    ],
    alerts: [],
    data_snapshot: { temperature: "30°C", aqi: 120, traffic_level: "Moderate", overall_rating: 8.5 }
  },
  Bangalore: {
    travel_score: 82,
    city: "Bangalore",
    start_coordinates: [12.9716, 77.5946],
    summary: "IT Hub with pleasant weather but severe traffic bottlenecks in ORR areas.",
    recommended_area: { name: "Indiranagar", safety_rating: 9, accessibility: "Moderate" },
    routes: [
      { id: "blr-r1", type: "Least Congested", time: "60 mins", risk_level: "Moderate", traffic_level: "High", description: "Avoid Silk Board; navigating backstreets required.", destination_coordinates: [12.9784, 77.6408] }
    ],
    stay_options: [
      { id: "blr-s1", name: "Tech Haven", rating: 4.5, price: 5000, summary: "Close to microbreweries and tech parks.", coordinates: [12.9716, 77.6411] }
    ],
    alerts: [{ id: "blr-a1", type: "warning", message: "Extreme traffic gridlocks during 6 PM - 9 PM." }],
    data_snapshot: { temperature: "25°C", aqi: 95, traffic_level: "High", overall_rating: 8.2 }
  },
  Chennai: {
    travel_score: 78,
    city: "Chennai",
    start_coordinates: [13.0827, 80.2707],
    summary: "Coastal warmth with moderate traffic. Ideal for cultural exploration.",
    recommended_area: { name: "Mylapore", safety_rating: 9, accessibility: "High" },
    routes: [
      { id: "che-r1", type: "Fastest", time: "25 mins", risk_level: "Safe", traffic_level: "Medium", description: "Clear routes along the coast.", destination_coordinates: [13.0333, 80.2667] }
    ],
    stay_options: [
      { id: "che-s1", name: "Marina View Inn", rating: 4.4, price: 3500, summary: "Affordable stay with ocean breeze.", coordinates: [13.0418, 80.2762] }
    ],
    alerts: [{ id: "che-a1", type: "info", message: "High humidity expected." }],
    data_snapshot: { temperature: "34°C", aqi: 85, traffic_level: "Moderate", overall_rating: 7.8 }
  },
  Kolkata: {
    travel_score: 80,
    city: "Kolkata",
    start_coordinates: [22.5726, 88.3639],
    summary: "City of Joy. Dense crowds but well-connected public transit.",
    recommended_area: { name: "Park Street", safety_rating: 8, accessibility: "High" },
    routes: [
      { id: "kol-r1", type: "Recommended", time: "40 mins", risk_level: "Safe", traffic_level: "Medium", description: "Use heritage tram/metro systems.", destination_coordinates: [22.5539, 88.3514] }
    ],
    stay_options: [
      { id: "kol-s1", name: "Heritage Manor", rating: 4.7, price: 6000, summary: "Classic colonial-era architecture.", coordinates: [22.5448, 88.3426] }
    ],
    alerts: [],
    data_snapshot: { temperature: "29°C", aqi: 150, traffic_level: "Moderate", overall_rating: 8.0 }
  },
  Hyderabad: {
    travel_score: 86,
    city: "Hyderabad",
    start_coordinates: [17.3850, 78.4867],
    summary: "Excellent blend of history and hyper-modern infrastructure.",
    recommended_area: { name: "Jubilee Hills", safety_rating: 9, accessibility: "High" },
    routes: [
      { id: "hyd-r1", type: "Fastest", time: "20 mins", risk_level: "Safe", traffic_level: "Low", description: "Wide ring roads provide rapid access.", destination_coordinates: [17.4326, 78.4071] }
    ],
    stay_options: [
      { id: "hyd-s1", name: "Cyber Inn", rating: 4.3, price: 4000, summary: "Perfect for business and leisure.", coordinates: [17.4436, 78.3773] }
    ],
    alerts: [],
    data_snapshot: { temperature: "31°C", aqi: 110, traffic_level: "Low", overall_rating: 8.6 }
  },
  Pune: {
    travel_score: 81,
    city: "Pune",
    start_coordinates: [18.5204, 73.8567],
    summary: "Pleasant climate, emerging IT sectors, and heavy two-wheeler traffic.",
    recommended_area: { name: "Koregaon Park", safety_rating: 9, accessibility: "Moderate" },
    routes: [
      { id: "pun-r1", type: "Safest", time: "35 mins", risk_level: "Moderate", traffic_level: "High", description: "Navigate carefully amidst heavy two-wheeler congestion.", destination_coordinates: [18.5362, 73.8940] }
    ],
    stay_options: [
      { id: "pun-s1", name: "Osho Retreat", rating: 4.8, price: 8000, summary: "Peaceful resort amidst city chaos.", coordinates: [18.5404, 73.8890] }
    ],
    alerts: [{ id: "pun-a1", type: "warning", message: "Unexpected localized traffic jams." }],
    data_snapshot: { temperature: "27°C", aqi: 85, traffic_level: "High", overall_rating: 8.1 }
  },
  Jaipur: {
    travel_score: 88,
    city: "Jaipur",
    start_coordinates: [26.9124, 75.7873],
    summary: "Pink City vibes with great heritage tourism. Traffic is dense in old city.",
    recommended_area: { name: "Civil Lines", safety_rating: 9, accessibility: "High" },
    routes: [
      { id: "jai-r1", type: "Least Congested", time: "20 mins", risk_level: "Safe", traffic_level: "Low", description: "Bypass old city walls for speedy transit.", destination_coordinates: [26.9239, 75.8267] }
    ],
    stay_options: [
      { id: "jai-s1", name: "Royal Palace Palace", rating: 4.9, price: 18000, summary: "Live like royalty.", coordinates: [26.8924, 75.8073] }
    ],
    alerts: [],
    data_snapshot: { temperature: "36°C", aqi: 130, traffic_level: "Moderate", overall_rating: 8.8 }
  },
  Goa: {
    travel_score: 92,
    city: "Goa",
    start_coordinates: [15.2993, 74.1240],
    summary: "Coastal paradise with very low traffic and excellent AQI.",
    recommended_area: { name: "Panaji", safety_rating: 9, accessibility: "High" },
    routes: [
      { id: "goa-r1", type: "Recommended", time: "15 mins", risk_level: "Safe", traffic_level: "Low", description: "Coastal highways are clear and scenic.", destination_coordinates: [15.4909, 73.8278] }
    ],
    stay_options: [
      { id: "goa-s1", name: "Beachfront Villa", rating: 4.8, price: 12000, summary: "Direct beach access.", coordinates: [15.5522, 73.7513] }
    ],
    alerts: [],
    data_snapshot: { temperature: "28°C", aqi: 45, traffic_level: "Low", overall_rating: 9.2 }
  },
  Leh: {
    travel_score: 95,
    city: "Leh",
    start_coordinates: [34.1526, 77.5771],
    summary: "High-altitude arid environment. Purest air quality but require acclimatization.",
    recommended_area: { name: "Leh Market", safety_rating: 9, accessibility: "Low" },
    routes: [
      { id: "leh-r1", type: "Safest", time: "10 mins", risk_level: "Moderate", traffic_level: "Low", description: "Steep drops; drive cautiously.", destination_coordinates: [34.1643, 77.5848] }
    ],
    stay_options: [
      { id: "leh-s1", name: "Himalayan Homestay", rating: 4.6, price: 2500, summary: "Authentic local experience with oxygen support.", coordinates: [34.1596, 77.5801] }
    ],
    alerts: [{ id: "leh-a1", type: "warning", message: "High altitude. Oxygen levels are 30% lower than sea level." }],
    data_snapshot: { temperature: "5°C", aqi: 10, traffic_level: "Low", overall_rating: 9.5 }
  }
};


// ----------------------------------------------------
// ADAPTER: BACKEND TO FRONTEND SCHEMA
// ----------------------------------------------------
const transformBackendResponse = (data: any, originalCity: string): AnalyzeResponse => {
  const mappedAlerts: Alert[] = (data.alerts || []).map((message: string, index: number) => ({
    id: `live-alert-${index}`,
    type: "warning",
    message
  }));

  const mappedStays: StayOption[] = (data.stay_options || []).map((stay: any, index: number) => ({
    id: `live-stay-${index}`,
    name: stay.name,
    rating: stay.rating,
    price: stay.price_per_night,
    summary: stay.budget_fit || "Standard stay" 
  }));

  const mappedRoutes: RouteOption[] = (data.routes || []).map((route: any, index: number) => {
    const routeTypeStr = route.type ? route.type.charAt(0).toUpperCase() + route.type.slice(1) : "Recommended";
    let mappedType: "Fastest" | "Safest" | "Least Congested" | "Recommended" = "Recommended";
    if (["Fastest", "Safest", "Least Congested", "Recommended"].includes(routeTypeStr)) {
      mappedType = routeTypeStr as "Fastest" | "Safest" | "Least Congested" | "Recommended";
    }

    let mappedTraffic: "Low" | "Medium" | "High" = "Medium";
    if (["Low", "Medium", "High"].includes(route.traffic_level)) {
      mappedTraffic = route.traffic_level as "Low" | "Medium" | "High";
    }

    return {
      id: `live-route-${index}`,
      type: mappedType,
      time: route.duration,
      risk_level: "Moderate", 
      traffic_level: mappedTraffic,
      description: `Travel path from ${route.from} to ${route.to} with ${route.traffic_level} traffic conditions.`
    };
  });

  let mappedTrafficLevel: "Low" | "Moderate" | "High" = "Moderate";
  const backendTraffic = data.data_snapshot?.traffic_overall;
  if (backendTraffic === "Low") mappedTrafficLevel = "Low";
  if (backendTraffic === "Medium" || backendTraffic === "Moderate") mappedTrafficLevel = "Moderate";
  if (backendTraffic === "High") mappedTrafficLevel = "High";

  const mappedSnapshot: DataSnapshot = {
    temperature: `${Math.round(data.data_snapshot?.weather?.temperature_c || 0)}°C`,
    aqi: data.data_snapshot?.aqi || 0,
    traffic_level: mappedTrafficLevel,
    overall_rating: Math.min((data.travel_score || 0) / 10, 10) 
  };

  return {
    travel_score: data.travel_score || 0,
    city: data.city || originalCity,
    summary: data.summary || "No summary available.",
    recommended_area: data.recommended_area || {},
    routes: mappedRoutes,
    stay_options: mappedStays,
    alerts: mappedAlerts,
    data_snapshot: mappedSnapshot,
    start_coordinates: data.start_coordinates 
  };
};

// ----------------------------------------------------
// HYBRID FETCH LOGIC (DEMO MOCK -> LIVE FALLBACK)
// ----------------------------------------------------
export const analyzeRequest = async (payload: AnalyzeRequest): Promise<AnalyzeResponse> => {
  // Normalize the user's city query
  const rawCity = payload.city.trim();
  const targetCity = rawCity.charAt(0).toUpperCase() + rawCity.slice(1).toLowerCase();

  // CHECK DEMO MODE: Fallback immediately if targetCity is in our 10-city Demo Map
  if (demoDataMap[targetCity]) {
    console.log(`[DEMO MODE] Intercepted payload. Loading demo data for ${targetCity}`);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ ...demoDataMap[targetCity] });
      }, 1500); 
    });
  }

  // CHECK LIVE BACKEND Fallback for non-demo cities
  console.log(`[HYBRID FETCH] City '${targetCity}' not strictly cached. Reaching out to live FastAPI backend...`);
  try {
    const response = await fetch("http://127.0.0.1:8001/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Backend Error Response:", errorText);
      throw new Error(`API returned status: ${response.status}`);
    }

    const json = await response.json();
    return transformBackendResponse(json, targetCity);

  } catch (error) {
    console.error("Failed to connect to generic intelligence network:", error);
    throw error; // Re-throw to trigger the frontend's SYSTEM FAILURE UI state
  }
};

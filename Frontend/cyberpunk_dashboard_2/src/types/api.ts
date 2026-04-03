export interface Preferences {
  safety_priority: number;
  cost_sensitivity: number;
  comfort_level: number;
  traffic_tolerance: number;
  pollution_tolerance: number;
  crowd_tolerance: number;
}

export interface AnalyzeRequest {
  city: string;
  trip_duration_days: number;
  total_budget: number;
  start_location: string;
  destination_type: string;
  preferences: Preferences;
}

export interface RouteOption {
  id: string;
  type: "Fastest" | "Safest" | "Least Congested" | "Recommended";
  time: string;
  risk_level: "Safe" | "Moderate" | "Risky";
  traffic_level: "Low" | "Medium" | "High";
  description: string;
  destination_coordinates?: [number, number];
}

export interface StayOption {
  id: string;
  name: string;
  rating: number;
  price: number;
  summary: string;
  coordinates?: [number, number];
}

export interface Alert {
  id: string;
  type: "warning" | "error" | "info";
  message: string;
}

export interface DataSnapshot {
  temperature: string;
  aqi: number;
  traffic_level: "Low" | "Moderate" | "High";
  overall_rating: number;
}

export interface AnalyzeResponse {
  travel_score: number;
  city: string;
  summary: string;
  recommended_area: Record<string, string | number | boolean>;
  routes: RouteOption[];
  stay_options: StayOption[];
  alerts: Alert[];
  data_snapshot: DataSnapshot;
  start_coordinates?: [number, number];
}

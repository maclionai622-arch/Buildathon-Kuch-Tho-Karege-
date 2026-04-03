import { useState, useCallback } from "react";
import type { AnalyzeRequest, AnalyzeResponse } from "../types/api";
import { analyzeRequest } from "../api/mockApi";

interface UseAnalysisState {
  loading: boolean;
  error: boolean;
  empty: boolean;
  data: AnalyzeResponse | null;
}

export const useAnalysis = () => {
  const [state, setState] = useState<UseAnalysisState>({
    loading: false,
    error: false,
    empty: true,
    data: null
  });

  const analyze = useCallback(async (payload: AnalyzeRequest) => {
    setState({ loading: true, error: false, empty: false, data: null });
    try {
      const result = await analyzeRequest(payload);
      
      // Strict contract mapping: catch nulls, map to empty arrays
      const strictResult: AnalyzeResponse = {
        travel_score: typeof result.travel_score === 'number' ? result.travel_score : 0,
        city: result.city || "Unknown",
        summary: result.summary || "No summary available.",
        recommended_area: result.recommended_area || {},
        routes: Array.isArray(result.routes) ? result.routes : [],
        stay_options: Array.isArray(result.stay_options) ? result.stay_options : [],
        alerts: Array.isArray(result.alerts) ? result.alerts : [],
        data_snapshot: result.data_snapshot || { temperature: "N/A", aqi: 0, traffic_level: "Low", overall_rating: 0 }
      };

      setState({
        loading: false,
        error: false,
        empty: false,
        data: strictResult
      });
    } catch {
      setState({
        loading: false,
        error: true,
        empty: false,
        data: null
      });
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      loading: false,
      error: false,
      empty: true,
      data: null
    });
  }, []);

  return { ...state, analyze, reset };
};

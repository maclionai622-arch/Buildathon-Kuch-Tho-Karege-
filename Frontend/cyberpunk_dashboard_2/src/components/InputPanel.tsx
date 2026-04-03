import { useState } from 'react';
import { GameSlider } from './GameSlider';
import type { AnalyzeRequest, Preferences } from '../types/api';
import { MapPin, Calendar, DollarSign, Target, Loader2 } from 'lucide-react';

interface InputPanelProps {
  onAnalyze: (payload: AnalyzeRequest) => void;
  loading: boolean;
}

const CITIES = ['Delhi', 'Mumbai', 'Kolkata', 'Hyderabad', 'Bangalore'];
const DESTINATION_TYPES = ['tourist', 'business', 'local', 'food', 'nightlife'];

export const InputPanel = ({ onAnalyze, loading }: InputPanelProps) => {
  const [city, setCity] = useState(CITIES[0]);
  const [duration, setDuration] = useState<number>(3);
  const [budget, setBudget] = useState<number>(6000);
  const [startLocation, setStartLocation] = useState('New Delhi Railway Station');
  const [destinationType, setDestinationType] = useState('tourist');
  
  const [preferences, setPreferences] = useState<Preferences>({
    safety_priority: 9,
    cost_sensitivity: 7,
    comfort_level: 6,
    traffic_tolerance: 3,
    pollution_tolerance: 4,
    crowd_tolerance: 5
  });

  const handleSliderChange = (key: keyof Preferences) => (val: number) => {
    setPreferences(prev => ({ ...prev, [key]: val }));
  };

  const handleLaunch = () => {
    onAnalyze({
      city,
      trip_duration_days: duration,
      total_budget: budget,
      start_location: startLocation,
      destination_type: destinationType,
      preferences
    });
  };

  return (
    <div className="flex flex-col gap-6 p-6 glass rounded-2xl neon-border h-full overflow-y-auto w-full max-w-sm">
      <div className="flex items-center gap-3 border-b border-white/10 pb-4">
        <Target className="text-neon-primary" size={24} />
        <h2 className="text-lg font-bold tracking-widest uppercase shadow-neon">Mission Parameters</h2>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label className="text-xs text-secondary font-mono">CITY REGION</label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" size={16} />
            <select 
              value={city} 
              onChange={(e) => setCity(e.target.value)}
              className="w-full bg-bg-input border border-white/10 rounded-md py-2 pl-10 pr-4 text-sm focus:border-neon-primary outline-none appearance-none cursor-pointer"
            >
              {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="flex flex-col gap-2 flex-1">
            <label className="text-xs text-secondary font-mono">DAYS</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" size={16} />
              <input 
                type="number" min={1} max={30} value={duration} onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full bg-bg-input border border-white/10 rounded-md py-2 pl-10 pr-4 text-sm focus:border-neon-primary outline-none"
              />
            </div>
          </div>
          <div className="flex flex-col gap-2 flex-1">
            <label className="text-xs text-secondary font-mono">BUDGET</label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" size={16} />
              <input 
                type="number" step={500} value={budget} onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full bg-bg-input border border-white/10 rounded-md py-2 pl-10 pr-4 text-sm focus:border-neon-primary outline-none"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-xs text-secondary font-mono">START LOCATION</label>
          <input 
            type="text" value={startLocation} onChange={(e) => setStartLocation(e.target.value)}
            className="w-full bg-bg-input border border-white/10 rounded-md py-2 px-4 text-sm focus:border-neon-primary outline-none"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-xs text-secondary font-mono">DESTINATION TYPE</label>
          <select 
            value={destinationType} 
            onChange={(e) => setDestinationType(e.target.value)}
            className="w-full bg-bg-input border border-white/10 rounded-md py-2 px-4 text-sm focus:border-neon-primary outline-none appearance-none cursor-pointer"
          >
            {DESTINATION_TYPES.map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}
          </select>
        </div>
      </div>

      <div className="mt-4 border-t border-white/10 pt-6 flex flex-col gap-4">
        <h3 className="text-xs font-bold text-accent-blue tracking-widest uppercase mb-2">Tactical Preferences</h3>
        
        <GameSlider label="Safety Priority" value={preferences.safety_priority} onChange={handleSliderChange('safety_priority')} />
        <GameSlider label="Cost Sens" value={preferences.cost_sensitivity} onChange={handleSliderChange('cost_sensitivity')} />
        <GameSlider label="Comfort" value={preferences.comfort_level} onChange={handleSliderChange('comfort_level')} />
        <GameSlider label="Traffic Tol" value={preferences.traffic_tolerance} onChange={handleSliderChange('traffic_tolerance')} />
        <GameSlider label="Pollution Tol" value={preferences.pollution_tolerance} onChange={handleSliderChange('pollution_tolerance')} />
        <GameSlider label="Crowd Tol" value={preferences.crowd_tolerance} onChange={handleSliderChange('crowd_tolerance')} />
      </div>

      <button 
        onClick={handleLaunch}
        disabled={loading}
        className="mt-6 w-full py-4 bg-neon-primary text-bg-primary font-black tracking-widest uppercase rounded-lg hover:bg-neon-secondary hover:shadow-[0_0_20px_var(--accent-glow)] transition-all flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Initializing...
          </>
        ) : (
          "Start Analysis"
        )}
      </button>
    </div>
  );
};

import { useRef, useState, useEffect } from 'react';
import { HeroSection } from './components/HeroSection';
import { InputPanel } from './components/InputPanel';
import { TravelScore } from './components/TravelScore';
import { LiveMap } from './components/LiveMap';
import { RouteMission } from './components/RouteMission';
import { AlertsPanel } from './components/AlertsPanel';
import { DataSnapshot } from './components/DataSnapshot';
import { useAnalysis } from './hooks/useAnalysis';
import { Loader2, AlertCircle, WifiOff } from 'lucide-react';
import './index.css';

// Memoize heavy UI components
// Removed MemoMapPanel reference

function App() {
  const { loading, error, empty, data, analyze } = useAnalysis();
  const [activeTarget, setActiveTarget] = useState<{
    coords: [number, number];
    type: "Fastest" | "Safest" | "Safehouse";
    id: string;
  } | null>(null);
  const dashboardRef = useRef<HTMLDivElement>(null);

  // Reset selection when new data arrives
  useEffect(() => {
    setActiveTarget(null);
  }, [data]);

  const scrollToDashboard = () => {
    dashboardRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary font-sans flex flex-col items-center overflow-x-hidden selection:bg-neon-primary selection:text-black">
      
      {/* Section 1: Hero Landing */}
      <HeroSection onStart={scrollToDashboard} />

      {/* Section 2: Dashboard Content */}
      <div 
        ref={dashboardRef}
        className="w-full flex flex-col items-center pt-20"
      >
        <header className="w-full max-w-7xl px-6 pb-12 flex flex-col items-center justify-center relative z-10">
          <div className="absolute top-0 left-0 w-full h-[30vh] bg-neon-primary/5 blur-[100px] pointer-events-none" />
          <h2 className="text-xl md:text-2xl font-mono tracking-[0.3em] uppercase text-secondary">
            Command Center
          </h2>
        </header>

        <main className="w-full max-w-7xl px-6 pb-24 flex flex-col lg:flex-row gap-8 relative z-10 flex-1">
          
          {/* Left Side: Input Panel */}
          <div className="w-full lg:w-1/3 shrink-0">
            <InputPanel onAnalyze={analyze} loading={loading} />
          </div>

          {/* Right Side: Dashboard Area */}
          <div className="w-full lg:w-2/3 flex flex-col gap-6">
            
            {/* Conditional States */}
            {loading && (
              <div className="flex-1 flex flex-col items-center justify-center glass rounded-2xl border border-neon-primary/30 min-h-[500px]">
                <Loader2 className="animate-spin text-neon-primary mb-4" size={48} />
                <h2 className="text-xl font-bold tracking-widest font-mono uppercase neon-text text-neon-primary animate-pulse">Analyzing City...</h2>
                <p className="text-secondary text-sm mt-2 font-mono">Running tactical permutations</p>
              </div>
            )}

            {error && !loading && (
              <div className="flex-1 flex flex-col items-center justify-center glass rounded-2xl border border-status-risky/50 min-h-[500px] bg-status-risky-light">
                <AlertCircle className="text-status-risky mb-4 animate-pulse-glow rounded-full" size={64} />
                <h2 className="text-3xl font-black tracking-widest font-mono uppercase text-status-risky" style={{ textShadow: '0 0 10px rgba(255,0,60,0.5)' }}>SYSTEM FAILURE</h2>
                <p className="text-white text-sm mt-2 font-mono">Unable to connect to intelligence network.</p>
              </div>
            )}

            {empty && !loading && !error && (
              <div className="flex-1 flex flex-col items-center justify-center glass rounded-2xl border border-white/10 min-h-[500px] opacity-70">
                <WifiOff className="text-secondary mb-4" size={48} />
                <h2 className="text-xl font-bold tracking-widest font-mono uppercase text-secondary">NO SIGNAL DETECTED</h2>
                <p className="text-secondary/50 text-xs mt-2 font-mono">Awaiting mission parameters...</p>
              </div>
            )}

            {data && !loading && !error && (
              <div className="flex flex-col gap-6 animate-slide-up">
                
                {/* Top Dashboard Row */}
                <div className="flex flex-col lg:flex-row gap-6">
                  <div className="w-full lg:w-1/2 flex items-center justify-center">
                    <TravelScore score={data.travel_score} />
                  </div>
                  <div className="w-full lg:w-1/2 flex flex-col gap-4">
                    <div className="glass p-4 rounded-xl border border-white/10">
                      <h3 className="text-xs text-secondary font-mono tracking-widest uppercase mb-1">AI Executive Summary</h3>
                      <p className="text-sm font-medium">{data.summary}</p>
                      <div className="mt-3 inline-block px-3 py-1 bg-white/5 border border-white/10 rounded text-xs text-accent-blue font-mono">
                        Target Area: {data.recommended_area.name} (Safety: {data.recommended_area.safety_rating})
                      </div>
                    </div>
                    {data.alerts && data.alerts.length > 0 && (
                      <AlertsPanel alerts={data.alerts} />
                    )}
                  </div>
                </div>

                {/* HUD Snapshot */}
                <DataSnapshot data={data.data_snapshot} />

                {/* Map & Routes */}
                <div className="flex flex-col xl:flex-row gap-6 mt-2">
                  <div className="w-full xl:w-2/3">
                    <LiveMap 
                      originCoords={data.start_coordinates || [28.6139, 77.2090]} 
                      activeTargetCoords={activeTarget?.coords}
                      activeTargetType={activeTarget?.type}
                    />
                  </div>
                  
                  <div className="w-full xl:w-1/3 flex flex-col gap-3">
                    <h3 className="text-xs font-bold font-mono tracking-widest uppercase text-secondary border-b border-white/10 pb-2">Available Missions</h3>
                    <div className="flex flex-col gap-3 overflow-y-auto max-h-[360px] pr-2">
                      {data.routes.map((route, idx) => (
                        <RouteMission 
                          key={route.id} 
                          route={route} 
                          index={idx} 
                          isActive={activeTarget?.id === route.id}
                          onClick={() => {
                            if (route.destination_coordinates) {
                              setActiveTarget(prev => prev?.id === route.id ? null : {
                                id: route.id,
                                coords: route.destination_coordinates!,
                                type: route.type === "Fastest" ? "Fastest" : "Safest"
                              });
                            }
                          }}
                        />
                      ))}
                      {data.routes.length === 0 && (
                        <p className="text-sm text-secondary font-mono">No valid routes detected.</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Stays Section */}
                <div className="mt-4">
                  <h3 className="text-xs font-bold font-mono tracking-widest uppercase text-secondary border-b border-white/10 pb-2 mb-4">Recommended Safehouses</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {data.stay_options.map((stay) => {
                      const isActive = activeTarget?.id === stay.id;
                      return (
                        <div 
                          key={stay.id} 
                          onClick={() => {
                            if (stay.coordinates) {
                              setActiveTarget(prev => prev?.id === stay.id ? null : {
                                id: stay.id,
                                coords: stay.coordinates!,
                                type: "Safehouse"
                              });
                            }
                          }}
                          className={`p-4 glass rounded-xl border ${isActive ? 'border-neon-primary ring-2 ring-neon-primary/50 bg-neon-primary/5' : 'border-white/10'} flex justify-between items-center group hover:border-white/30 transition-all cursor-pointer`}
                        >
                          <div>
                            <h4 className={`font-bold text-sm ${isActive ? 'text-neon-primary' : 'text-white'} group-hover:text-neon-primary transition-colors`}>{stay.name}</h4>
                            <p className="text-xs text-secondary mt-1">{stay.summary}</p>
                          </div>
                          <div className="flex flex-col items-end">
                            <span className="text-lg font-black font-mono">${stay.price}</span>
                            <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-accent-yellow mt-1">★ {stay.rating}</span>
                          </div>
                        </div>
                      );
                    })}
                    {data.stay_options.length === 0 && (
                      <p className="text-sm text-secondary font-mono">No safehouses matched criteria.</p>
                    )}
                  </div>
                </div>

              </div>
            )}

          </div>
        </main>
      </div>

    </div>
  );
}

export default App;

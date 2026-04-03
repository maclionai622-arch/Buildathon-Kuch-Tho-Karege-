import type { RouteOption } from '../types/api';
import { Zap, ShieldCheck, CarFront, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface RouteMissionProps {
  route: RouteOption;
  index: number;
  onClick?: () => void;
  isActive?: boolean;
}

export const RouteMission = ({ route, index, onClick, isActive }: RouteMissionProps) => {
  const getIcon = () => {
    switch(route.type) {
      case "Fastest": return <Zap className="text-accent-yellow" size={18} />;
      case "Safest": return <ShieldCheck className="text-status-safe" size={18} />;
      case "Least Congested": return <CarFront className="text-accent-blue" size={18} />;
      default: return <CheckCircle2 className="text-white" size={18} />;
    }
  };

  const getRiskColor = (risk: string) => {
    switch(risk) {
      case "Safe": return "text-status-safe bg-status-safe-light border-status-safe";
      case "Moderate": return "text-status-moderate bg-status-moderate-light border-status-moderate";
      case "Risky": return "text-status-risky bg-status-risky-light border-status-risky";
      default: return "text-white bg-white/10 border-white/20";
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 * index }}
      onClick={onClick}
      className={`relative p-4 rounded-xl border transition-all cursor-pointer overflow-hidden group glass ${
        isActive 
          ? 'border-neon-primary ring-2 ring-neon-primary/50 bg-neon-primary/5 shadow-[0_0_15px_rgba(20,255,236,0.2)]' 
          : 'border-white/10 hover:border-white/30'
      }`}
    >
      {/* Recommended badge hook logic (we mock it for the first one if Recommended is not explicitly set) */}
      {route.type === "Safest" && (
        <div className="absolute top-0 right-0 bg-status-safe text-bg-primary text-[10px] font-bold px-2 py-1 tracking-wider uppercase rounded-bl-lg z-10">
          Recommended
        </div>
      )}

      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-bg-input rounded-lg border border-white/5 group-hover:scale-110 transition-transform">
            {getIcon()}
          </div>
          <div>
            <h3 className={`font-bold text-sm tracking-wide ${isActive ? 'text-neon-primary' : 'text-white'}`}>{route.type} Mission</h3>
            <p className="text-xs text-secondary">{route.time} ETE</p>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-300 mb-4">{route.description}</p>

      <div className="flex items-center gap-2">
        <span className={`text-xs px-2 py-1 rounded border ${getRiskColor(route.risk_level)}`}>
          Risk: {route.risk_level}
        </span>
        <span className="text-xs px-2 py-1 rounded border border-white/10 bg-bg-input text-secondary">
          Traffic: {route.traffic_level}
        </span>
      </div>
    </motion.div>
  );
};

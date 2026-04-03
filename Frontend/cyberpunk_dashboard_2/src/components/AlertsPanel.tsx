import type { Alert } from '../types/api';
import { AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

interface AlertsPanelProps {
  alerts: Alert[];
}

export const AlertsPanel = ({ alerts }: AlertsPanelProps) => {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      {alerts.map((alert, idx) => (
        <motion.div 
          key={alert.id || idx}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="relative p-4 bg-status-risky-light border-l-4 border-status-risky rounded-r-lg shadow-[0_0_15px_rgba(255,0,60,0.3)] overflow-hidden"
        >
          <div className="absolute inset-0 bg-status-risky/10 animate-pulse pointer-events-none" />
          
          <div className="flex items-start gap-3 relative z-10">
            <AlertTriangle className="text-status-risky shrink-0 mt-0.5 animate-pulse-glow rounded-full" size={20} />
            <div>
              <h4 className="text-status-risky font-bold text-xs tracking-widest uppercase mb-1 font-mono">
                [⚠ SYSTEM ALERT]
              </h4>
              <p className="text-sm font-medium text-white">{alert.message}</p>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

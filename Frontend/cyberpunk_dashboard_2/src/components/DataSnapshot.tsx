import type { DataSnapshot as DataSnapshotType } from '../types/api';
import { Thermometer, Wind, Car, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

interface DataSnapshotProps {
  data: DataSnapshotType;
}

export const DataSnapshot = ({ data }: DataSnapshotProps) => {
  const stats = [
    { label: 'TEMP', value: data.temperature, icon: <Thermometer size={14} className="text-neon-primary" />, color: 'border-neon-primary glow-neon' },
    { label: 'AQI', value: data.aqi, icon: <Wind size={14} className="text-accent-blue" />, color: 'border-accent-blue glow-blue' },
    { label: 'TRAFFIC', value: data.traffic_level, icon: <Car size={14} className="text-status-risky" />, color: 'border-status-risky glow-red' },
    { label: 'RATING', value: `${data.overall_rating}/10`, icon: <Activity size={14} className="text-accent-yellow" />, color: 'border-accent-yellow glow-yellow' },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {stats.map((stat, idx) => (
        <motion.div 
          key={stat.label}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 + (idx * 0.1) }}
          className="flex items-center gap-3 p-3 bg-bg-card border border-white/10 rounded-lg glass"
        >
          <div className={`p-2 rounded border ${stat.color} bg-black/50`}>
            {stat.icon}
          </div>
          <div>
            <div className="text-[10px] font-mono tracking-widest text-secondary uppercase">{stat.label}</div>
            <div className="text-sm font-bold">{stat.value}</div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

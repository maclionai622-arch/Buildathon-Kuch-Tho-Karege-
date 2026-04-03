import { MapPin } from 'lucide-react';
import { motion } from 'framer-motion';

export const MapPanel = () => {
  return (
    <div className="relative w-full h-[400px] bg-bg-primary rounded-2xl overflow-hidden neon-border">
      {/* CSS Grid Background */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: 'linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)',
          backgroundSize: '40px 40px'
        }}
      />
      
      {/* Scanning effect */}
      <div className="absolute inset-0 scanline animate-[slide-up_4s_ease-in-out_infinite_alternate]" />

      {/* Color Zones */}
      <div className="absolute top-[20%] left-[20%] w-[40%] h-[50%] bg-status-safe-light rounded-[40%] blur-3xl" />
      <div className="absolute bottom-[20%] right-[10%] w-[30%] h-[40%] bg-status-risky-light rounded-[30%] blur-3xl animate-pulse" />

      {/* SVG Animated Routes */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none">
        {/* Main Route */}
        <motion.path 
          d="M 100,300 Q 250,200 400,150 T 700,100" 
          fill="none" 
          stroke="var(--color-neon-primary)" 
          strokeWidth="4"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: "easeInOut" }}
          style={{ filter: "drop-shadow(0 0 8px var(--color-neon-primary))" }}
        />
        {/* Alt Route */}
        <path 
          d="M 100,300 Q 300,350 450,250 T 700,100" 
          fill="none" 
          stroke="rgba(0, 240, 255, 0.4)" 
          strokeWidth="2"
          strokeDasharray="8,8"
        />
      </svg>

      {/* Neon Dots (Locations) */}
      <div className="absolute top-[300px] left-[100px] -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        <div className="absolute w-8 h-8 rounded-full bg-accent-blue/20 animate-ping" />
        <div className="w-4 h-4 rounded-full bg-accent-blue border border-white shadow-[0_0_15px_var(--color-accent-blue)] z-10" />
        <span className="absolute top-6 text-[10px] font-mono tracking-widest bg-bg-card/80 px-2 rounded border border-white/10 uppercase">Origin</span>
      </div>

      <div className="absolute top-[100px] left-[700px] -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        <div className="absolute w-12 h-12 rounded-full bg-neon-primary/20 animate-pulse" />
        <div className="w-6 h-6 rounded-full bg-bg-card border-2 border-neon-primary shadow-[0_0_15px_var(--color-neon-primary)] flex items-center justify-center z-10">
          <MapPin size={14} className="text-neon-primary" />
        </div>
        <span className="absolute top-8 text-[10px] font-mono tracking-widest bg-bg-card/80 px-2 rounded border border-white/10 uppercase neon-text text-neon-primary">Dest</span>
      </div>
    </div>
  );
};

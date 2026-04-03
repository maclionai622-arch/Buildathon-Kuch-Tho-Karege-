import { motion } from 'framer-motion';

interface GameSliderProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  onChange: (val: number) => void;
}

export const GameSlider = ({ label, value, min = 1, max = 10, onChange }: GameSliderProps) => {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className="flex flex-col gap-2 w-full mb-4">
      <div className="flex justify-between items-center">
        <label className="text-xs font-mono uppercase tracking-wider text-secondary">
          {label}
        </label>
        <span className="text-xs font-bold neon-text text-primary">
          {value} <span className="text-secondary opacity-50">/ {max}</span>
        </span>
      </div>

      <div className="relative h-6 flex items-center w-full group">
        {/* Track Background */}
        <div className="absolute w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
          <div className="scanline absolute inset-0 opacity-20" />
        </div>
        
        {/* Active Track (Neon) */}
        <motion.div 
          className="absolute h-2 bg-neon-primary rounded-full transition-all duration-150"
          style={{ width: `${percentage}%`, backgroundColor: 'var(--color-neon-primary)', boxShadow: '0 0 10px var(--accent-glow)' }}
        />

        {/* The Native Input Slider - Invisible but handles events */}
        <input 
          type="range" 
          min={min} 
          max={max} 
          value={value} 
          onChange={(e) => onChange(Number(e.target.value))}
          className="absolute w-full h-full opacity-0 cursor-pointer z-10"
        />

        {/* Custom Thumb */}
        <motion.div 
          className="absolute w-4 h-6 bg-white rounded-sm pointer-events-none group-hover:scale-110 transition-transform"
          style={{ 
            left: `calc(${percentage}% - 8px)`,
            boxShadow: '0 0 10px var(--color-neon-primary), 0 0 20px rgba(255,255,255,0.5)',
            border: '1px solid var(--color-neon-primary)'
          }}
        >
          <div className="w-full h-full flex flex-col items-center justify-center gap-[2px]">
            <div className="w-2 h-[1px] bg-zinc-400" />
            <div className="w-2 h-[1px] bg-zinc-400" />
            <div className="w-2 h-[1px] bg-zinc-400" />
          </div>
        </motion.div>
      </div>
    </div>
  );
};

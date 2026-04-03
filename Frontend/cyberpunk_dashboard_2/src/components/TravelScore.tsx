import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface TravelScoreProps {
  score: number;
}

export const TravelScore = ({ score }: TravelScoreProps) => {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const increment = score / (duration / 16); // 60fps approx

    const animateNumber = () => {
      start += increment;
      if (start < score) {
        setDisplayScore(Math.floor(start));
        requestAnimationFrame(animateNumber);
      } else {
        setDisplayScore(score);
      }
    };
    requestAnimationFrame(animateNumber);
  }, [score]);

  // Determine color and glow based on score
  let color = 'var(--color-status-risky)';
  let glow = 'rgba(255, 0, 60, 0.4)';
  if (score >= 70) {
    color = 'var(--color-status-safe)';
    glow = 'var(--accent-glow)';
  } else if (score >= 40) {
    color = 'var(--color-status-moderate)';
    glow = 'var(--color-status-moderate-light)';
  }

  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-6 glass rounded-2xl neon-border-blue w-full max-w-sm mx-auto">
      <h2 className="text-sm tracking-widest text-secondary font-mono mb-6 uppercase">Travel Intelligence Score</h2>
      
      <div className="relative flex items-center justify-center" style={{ width: 220, height: 220 }}>
        {/* Background glow circle */}
        <div 
          className="absolute inset-0 rounded-full blur-xl" 
          style={{ backgroundColor: glow, opacity: 0.6, transform: 'scale(0.8)' }}
        />
        
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 220 220">
          <circle
            cx="110"
            cy="110"
            r={radius}
            fill="none"
            stroke="var(--color-bg-input)"
            strokeWidth="8"
          />
          <motion.circle
            cx="110"
            cy="110"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{ strokeDasharray: circumference, filter: `drop-shadow(0 0 10px ${color})` }}
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-6xl font-black" style={{ color, textShadow: `0 0 20px ${glow}` }}>
            {displayScore}
          </span>
          <span className="text-xs text-secondary font-mono mt-1">/ 100</span>
        </div>
      </div>
    </div>
  );
};

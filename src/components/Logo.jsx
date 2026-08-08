import React from 'react';

/**
 * TrustShield AI Logo Component
 * Modern high-tech emblem featuring a cyber-shield vector and financial node network.
 */
export const Logo = ({ size = "normal", showSubtitle = true, onClick }) => {
  const isSmall = size === "small";

  return (
    <div 
      className="flex items-center gap-3 cursor-pointer select-none group"
      onClick={onClick}
    >
      {/* Emblem Container */}
      <div className={`relative ${isSmall ? 'w-8 h-8' : 'w-10 h-10'} rounded-xl bg-linear-to-br from-[#206a5e] via-[#104b42] to-[#095c51] p-2 flex items-center justify-center shadow-lg border border-[#a9f0e0]/40 group-hover:border-[#a9f0e0] group-hover:scale-105 transition-all duration-300 shrink-0`}>
        {/* Glowing aura backdrop */}
        <div className="absolute inset-0 bg-[#a9f0e0]/20 rounded-xl blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          className="w-full h-full text-[#a9f0e0] relative z-10" 
          stroke="currentColor" 
          strokeWidth="1.8" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          {/* Shield Outline */}
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" className="drop-shadow-sm" />
          
          {/* Central AI Node Grid */}
          <circle cx="12" cy="11" r="2.5" fill="#a9f0e0" fillOpacity="0.3" stroke="#a9f0e0" strokeWidth="2" />
          <path d="M12 8.5V5" strokeWidth="1.5" />
          <path d="M12 13.5V17" strokeWidth="1.5" />
          <path d="M9.5 11H7" strokeWidth="1.5" />
          <path d="M14.5 11H17" strokeWidth="1.5" />
          
          {/* Outer corner nodes */}
          <circle cx="7" cy="11" r="1" fill="#a9f0e0" />
          <circle cx="17" cy="11" r="1" fill="#a9f0e0" />
          <circle cx="12" cy="5" r="1" fill="#a9f0e0" />
        </svg>
      </div>

      {/* Brand Text Column */}
      <div>
        <h1 className={`font-display-lg ${isSmall ? 'text-lg' : 'text-xl'} font-bold text-[#206a5e] dark:text-[#a9f0e0] tracking-tight flex items-center gap-1.5 leading-none`}>
          TrustShield <span className="text-[#095c51] dark:text-[#a9f0e0] font-mono text-xs px-1.5 py-0.5 rounded bg-[#a9f0e0] dark:bg-[#206a5e] font-bold border border-[#206a5e]/30">AI</span>
        </h1>
        {showSubtitle && (
          <p className="hidden lg:block text-[9px] font-data-mono theme-text-muted tracking-wider uppercase mt-1">
            SEBI Financial Trust & Fraud Intelligence Platform
          </p>
        )}
      </div>
    </div>
  );
};

export default Logo;

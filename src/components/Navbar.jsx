import React from 'react';
import Logo from './Logo';
import { GlowButton } from '@/components/unlumen-ui/primitives/glow';
import { ThemeSwitch } from '@/components/unlumen-ui/primitives/theme-switch';
import { Highlight, HighlightItem } from '@/components/unlumen-ui/primitives/highlight';

export default function Navbar({ activeTab, setActiveTab, isDark, toggleTheme }) {
  return (
    <header className="sticky top-0 z-50 flex justify-between items-center px-6 h-16 theme-surface-dim backdrop-blur-xl border-b theme-border shadow-md transition-colors duration-300">
      {/* Brand Logo & Name */}
      <Logo onClick={() => setActiveTab('home')} />

      {/* Navigation Links using Highlight Primitive */}
      <nav className="hidden md:flex items-center">
        <Highlight
          value={activeTab}
          onChange={setActiveTab}
          hover={true}
          containerClassName="flex items-center gap-1 p-1 rounded-xl theme-surface-low border theme-border"
        >
          <HighlightItem value="home" className="px-3.5 py-1.5 rounded-lg font-label-caps text-xs">
            Home
          </HighlightItem>

          <HighlightItem value="threat_intel" className="px-3.5 py-1.5 rounded-lg font-label-caps text-xs">
            Threat Intelligence
          </HighlightItem>

          <HighlightItem value="analysis_nexus" className="px-3.5 py-1.5 rounded-lg font-label-caps text-xs">
            Analysis Nexus
          </HighlightItem>

          <HighlightItem value="investigations" className="px-3.5 py-1.5 rounded-lg font-label-caps text-xs">
            Investigations
          </HighlightItem>
        </Highlight>
      </nav>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Light / Dark Mode Animated Toggle Switch */}
        <ThemeSwitch isDark={isDark} toggleTheme={toggleTheme} iconSize={14} />

        <button 
          onClick={() => setActiveTab('threat_intel')}
          className="material-symbols-outlined text-[#727d7a] hover:text-[#206a5e] transition cursor-pointer"
          title="Notifications"
        >
          notifications
        </button>

        <GlowButton 
          onClick={() => setActiveTab('threat_intel')}
          mode="rotate"
          blur="medium"
          duration={5}
          colors={["#206a5e", "#a9f0e0", "#326677"]}
          className="px-3.5! py-1.5! text-xs! font-mono! uppercase tracking-wider"
        >
          ACCESS SYSTEM
        </GlowButton>
      </div>
    </header>
  );
}

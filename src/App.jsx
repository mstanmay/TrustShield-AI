import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingView from './components/LandingView';
import ThreatIntelView from './components/ThreatIntelView';
import AnalysisNexusView from './components/AnalysisNexusView';
import ComplaintAssistantView from './components/ComplaintAssistantView';
import TextRevealDemo from './components/TextRevealDemo';
import GlowButtonDemo from './components/GlowButtonDemo';
import Footer from './components/Footer';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [isDark, setIsDark] = useState(true); // Default to Dark Mode so user sees full cover background immediately

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(prev => !prev);
  };

  return (
    <div className="min-h-screen relative theme-text flex flex-col font-body-lg selection:bg-[#206a5e] selection:text-white transition-colors duration-300">
      
      {/* Fixed Full-Cover Background Image Layer (Spans behind ALL pages in both Light & Dark modes) */}
      <div className="global-bg-container">
        <div className="global-bg-overlay"></div>
      </div>

      {/* Top Navbar */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isDark={isDark} 
        toggleTheme={toggleTheme} 
      />

      {/* Main Content Body */}
      <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
        {activeTab === 'home' && (
          <LandingView setActiveTab={setActiveTab} />
        )}

        {activeTab === 'threat_intel' && (
          <ThreatIntelView setActiveTab={setActiveTab} />
        )}

        {activeTab === 'analysis_nexus' && (
          <AnalysisNexusView setActiveTab={setActiveTab} />
        )}

        {activeTab === 'investigations' && (
          <ComplaintAssistantView />
        )}

        {activeTab === 'text_reveal' && (
          <TextRevealDemo />
        )}

        {activeTab === 'glow_demo' && (
          <GlowButtonDemo />
        )}
      </main>

      {/* Footer */}
      <Footer setActiveTab={setActiveTab} />

    </div>
  );
}

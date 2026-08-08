import React, { useState } from 'react';
import { TextReveal } from '@/components/unlumen-ui/primitives/text-reveal';
import { GlowButton } from '@/components/unlumen-ui/primitives/glow';
import { FaviconSearch } from '@/components/unlumen-ui/primitives/favicon-search';
import { ClippedCircle } from '@/components/unlumen-ui/primitives/clipped-circle';
import { Highlight, HighlightItem } from '@/components/unlumen-ui/primitives/highlight';

export default function ThreatIntelView({ setActiveTab }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const alerts = [
    {
      id: 'ALT-7842',
      time: '15:14:02 IST',
      security: 'XYZTECH (NSE)',
      signal: 'Social Hype & Order Spike (Pump & Dump)',
      severity: 'CRITICAL',
      score: 94,
      details: 'Unusual social volume (+840% Telegram channels) preceding order placement of 4.2M shares across 12 coordinated retail broker accounts.',
      shap: 'Telegram sentiment velocity (+48%)'
    },
    {
      id: 'ALT-7841',
      time: '15:11:45 IST',
      security: 'ADANIENT (NSE)',
      signal: 'Circular Wash Trading Loop',
      severity: 'HIGH',
      score: 82,
      details: '4 Broker sub-entities detected executing synchronized buy/sell orders within 250ms window with zero change in beneficial ownership.',
      shap: 'Synchronized trade timing (+34%)'
    },
    {
      id: 'ALT-7840',
      time: '15:08:12 IST',
      security: 'TATAMOTORS (NSE)',
      signal: 'Insider Trading Block Anomaly',
      severity: 'HIGH',
      score: 74,
      details: 'Off-market block transfer executed 2 hours prior to quarterly board announcement by promoter-affiliated entity.',
      shap: 'Off-market transfer timing (+28%)'
    },
    {
      id: 'ALT-7839',
      time: '14:55:30 IST',
      security: 'HDFCBANK (NSE)',
      signal: 'Order Book Spoofing Signal',
      severity: 'MEDIUM',
      score: 68,
      details: 'Large bid orders placed at Depth-5 and canceled prior to execution (89% cancellation rate).',
      shap: 'Order cancellation velocity (+22%)'
    }
  ];

  const filteredAlerts = alerts.filter((alt) => {
    const matchesSearch = alt.security.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          alt.signal.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (!matchesSearch) return false;

    if (categoryFilter === 'critical') return alt.severity === 'CRITICAL';
    if (categoryFilter === 'insider') return alt.signal.toLowerCase().includes('insider');
    if (categoryFilter === 'social') return alt.signal.toLowerCase().includes('pump') || alt.signal.toLowerCase().includes('social');
    
    return true;
  });

  return (
    <div className="space-y-8 py-8 relative z-10">
      
      {/* Header Banner */}
      <div className="theme-surface p-6 rounded-3xl border theme-border flex flex-wrap items-center justify-between gap-4 alpine-shadow">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#206a5e] text-2xl">radar</span>
            <TextReveal
              text="Threat Intelligence Stream"
              as="h2"
              splitBy="words"
              staggerDelay={0.04}
              duration={0.4}
              className="font-display-lg text-2xl font-bold text-[#206a5e]"
            />
            <span className="font-data-mono text-xs px-2.5 py-0.5 rounded bg-[#a9f0e0] text-[#095c51] font-bold">
              LIVE SURVEILLANCE
            </span>
          </div>
          <TextReveal
            text="Real-time algorithmic stream scanning NSE/BSE securities for market manipulation & abnormal trading behavior."
            as="p"
            splitBy="words"
            staggerDelay={0.02}
            duration={0.3}
            className="font-body-sm text-xs theme-text-muted block"
          />
        </div>

        <div className="flex items-center gap-3">
          <GlowButton 
            onClick={() => setActiveTab('analysis_nexus')}
            mode="rotate"
            blur="medium"
            duration={4}
            colors={["#206a5e", "#a9f0e0", "#326677"]}
            className="px-4! py-2.5! text-xs! font-data-mono! font-bold"
          >
            Launch Analysis Nexus →
          </GlowButton>
        </div>
      </div>

      {/* Grid: Surveillance Table & Alerts */}
      <div className="grid lg:grid-cols-12 gap-8">
        
        {/* Left 7 Columns: Market Surveillance Stream */}
        <div className="lg:col-span-7 space-y-6">
          <div className="relative overflow-hidden theme-surface p-6 rounded-3xl border theme-border alpine-shadow space-y-4 group">
            <ClippedCircle circleSize={340} circleClassName="bg-[#206a5e]/20" />
            
            <div className="flex justify-between items-center border-b theme-border pb-3">
              <span className="font-display-lg text-lg font-bold text-[#206a5e]">Market Security Monitor</span>
              <span className="font-data-mono text-xs theme-text-muted">UPDATED: JUST NOW</span>
            </div>

            {/* Filter Input with Favicon Search */}
            <FaviconSearch
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Search security ticker or domain (e.g. nseindia.com, bseindia.com)..."
              className="max-w-none"
            />

            {/* Category Filter Pills using Highlight Primitive */}
            <Highlight
              hover={true}
              value={categoryFilter}
              onChange={setCategoryFilter}
              containerClassName="flex items-center gap-1.5 p-1 theme-surface-low rounded-xl border theme-border overflow-x-auto text-[11px] font-mono"
            >
              {[
                { id: "all", label: "ALL THREATS" },
                { id: "critical", label: "CRITICAL" },
                { id: "insider", label: "INSIDER TRADING" },
                { id: "social", label: "PUMP & DUMP" },
              ].map((pill) => (
                <HighlightItem
                  key={pill.id}
                  value={pill.id}
                  className="px-3 py-1.5 rounded-lg font-bold transition-colors"
                >
                  <span>{pill.label}</span>
                </HighlightItem>
              ))}
            </Highlight>

            {/* Alert List */}
            <div className="space-y-3 font-mono text-xs">
              {filteredAlerts.length === 0 ? (
                <div className="p-8 text-center theme-text-muted text-xs font-mono border theme-border rounded-2xl">
                  No threat alerts matched the selected category or search ticker.
                </div>
              ) : (
                filteredAlerts.map((alt) => (
                  <div 
                    key={alt.id}
                    className="p-4 theme-surface-card rounded-2xl border theme-border hover:border-[#206a5e] transition space-y-2 cursor-pointer"
                    onClick={() => setActiveTab('analysis_nexus')}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-[#095c51] bg-[#a9f0e0] px-2 py-0.5 rounded text-[10px]">{alt.id} • {alt.time}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        alt.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-600 border border-red-500/40 animate-pulse' : 'bg-amber-500/20 text-amber-700'
                      }`}>
                        {alt.severity} ({alt.score}%)
                      </span>
                    </div>

                    <h4 className="font-display-lg text-base font-bold theme-text">{alt.security}</h4>
                    <p className="font-body-sm text-xs theme-text-muted">{alt.signal}</p>

                    <div className="pt-2 border-t theme-border flex justify-between text-[11px] theme-text-muted">
                      <span>SHAP: {alt.shap}</span>
                      <span className="text-[#206a5e] font-bold hover:underline">Inspect Graph →</span>
                    </div>
                  </div>
                ))
              )}
            </div>

          </div>
        </div>

        {/* Right 5 Columns: Heatmap & System Health */}
        <div className="lg:col-span-5 space-y-6">
          <div className="theme-surface p-6 rounded-3xl border theme-border alpine-shadow space-y-4">
            <div className="flex justify-between items-center border-b theme-border pb-3">
              <span className="font-display-lg text-lg font-bold text-[#206a5e]">Sector Volatility Heatmap</span>
              <span className="font-data-mono text-xs text-emerald-600 font-bold">OPERATIONAL</span>
            </div>

            <div className="grid grid-cols-2 gap-3 font-data-mono text-xs text-center">
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-600">
                <p className="font-bold text-sm">SMALLCAP</p>
                <p className="text-[10px]">RISK: 91%</p>
              </div>
              <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl text-amber-700">
                <p className="font-bold text-sm">FINTECH</p>
                <p className="text-[10px]">RISK: 74%</p>
              </div>
              <div className="p-4 theme-surface-low border theme-border rounded-2xl text-cyan-600">
                <p className="font-bold text-sm">NIFTY 50</p>
                <p className="text-[10px]">RISK: 14%</p>
              </div>
              <div className="p-4 theme-surface-low border theme-border rounded-2xl text-emerald-600">
                <p className="font-bold text-sm">IT SECTOR</p>
                <p className="text-[10px]">RISK: 08%</p>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}

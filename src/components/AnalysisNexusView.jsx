import React, { useState } from 'react';
import { TextReveal } from '@/components/unlumen-ui/primitives/text-reveal';
import { GlowButton } from '@/components/unlumen-ui/primitives/glow';
import { ClippedCircle } from '@/components/unlumen-ui/primitives/clipped-circle';

export default function AnalysisNexusView({ setActiveTab }) {
  const [selectedEntity, setSelectedEntity] = useState({
    id: 'ENT-8942',
    name: 'Apex Capital FPI (Mauritius Ltd)',
    type: 'Foreign Portfolio Investor',
    riskScore: 88,
    sharedIPs: 18,
    connectedBrokers: 4,
    recentVolume: '₹148.5 Crore',
    flaggedReason: 'Synchronized off-market transfers preceding XYZTECH earnings release'
  });

  const nodes = [
    { id: 'ENT-8942', name: 'Apex Capital FPI', type: 'FPI Entity', risk: 88, color: 'bg-red-500', x: '25%', y: '35%' },
    { id: 'ENT-3310', name: 'Retail Aggregator #4', type: 'Broker Sub-Account', risk: 74, color: 'bg-amber-500', x: '60%', y: '25%' },
    { id: 'ENT-9012', name: 'Telegram "Bulls_Hub"', type: 'Social Group', risk: 94, color: 'bg-red-600', x: '40%', y: '65%' },
    { id: 'ENT-1104', name: 'Promoter Shell Corp', type: 'Promoter Entity', risk: 82, color: 'bg-amber-500', x: '75%', y: '55%' },
    { id: 'ENT-[#001]', name: 'XYZTECH Security', type: 'Target Stock', risk: 94, color: 'bg-[#206a5e]', x: '50%', y: '45%' },
  ];

  return (
    <div className="space-y-8 py-8 relative z-10">
      
      {/* Header Banner */}
      <div className="theme-surface p-6 rounded-3xl border theme-border flex flex-wrap items-center justify-between gap-4 alpine-shadow">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#206a5e] text-2xl">hub</span>
            <TextReveal
              text="Analysis Nexus & XAI Forensics"
              as="h2"
              splitBy="words"
              staggerDelay={0.04}
              duration={0.4}
              className="font-display-lg text-2xl font-bold text-[#206a5e]"
            />
            <span className="font-data-mono text-xs px-2.5 py-0.5 rounded bg-[#a9f0e0] text-[#095c51] font-bold">
              CROSS-MARKET GRAPH
            </span>
          </div>
          <TextReveal
            text="Visualizing multi-entity trade synchronization, shared IP clusters & Explainable AI (XAI) feature attribution."
            as="p"
            splitBy="words"
            staggerDelay={0.02}
            duration={0.3}
            className="font-body-sm text-xs theme-text-muted block"
          />
        </div>

        <div className="flex items-center gap-3">
          <GlowButton 
            onClick={() => alert('Exporting full TrustShield Evidence Dossier...')}
            mode="rotate"
            blur="medium"
            duration={4}
            colors={["#206a5e", "#a9f0e0", "#326677"]}
            className="px-4! py-2.5! text-xs! font-data-mono! font-bold"
          >
            Export Evidence Dossier →
          </GlowButton>
        </div>
      </div>

      {/* Main Grid: Interactive Canvas & Entity Card */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left 8 Columns: Entity Relationship Graph Visualizer */}
        <div className="lg:col-span-8 theme-surface p-6 rounded-3xl border theme-border space-y-4 alpine-shadow">
          <div className="flex items-center justify-between border-b theme-border pb-3">
            <div className="flex items-center gap-2 font-mono text-xs text-[#206a5e] font-bold">
              <span className="w-2 h-2 rounded-full bg-[#206a5e] animate-ping"></span>
              <span>CROSS-MARKET ENTITY GRAPH VISUALIZER</span>
            </div>
            <span className="text-[10px] font-mono theme-text-muted">5 ACTIVE GRAPH NODES</span>
          </div>

          {/* Interactive Graph Canvas Area */}
          <div className="relative h-105 rounded-2xl overflow-hidden theme-surface-low border theme-border p-4">
            
            {/* SVG Connecting Edges */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              <line x1="25%" y1="35%" x2="50%" y2="45%" stroke="rgba(239, 68, 68, 0.6)" strokeWidth="2" strokeDasharray="4 2" />
              <line x1="60%" y1="25%" x2="50%" y2="45%" stroke="rgba(245, 158, 11, 0.6)" strokeWidth="2" />
              <line x1="40%" y1="65%" x2="50%" y2="45%" stroke="rgba(32, 106, 94, 0.7)" strokeWidth="2.5" />
              <line x1="75%" y1="55%" x2="50%" y2="45%" stroke="rgba(245, 158, 11, 0.6)" strokeWidth="2" />
              <line x1="25%" y1="35%" x2="40%" y2="65%" stroke="rgba(168, 85, 247, 0.6)" strokeWidth="2" strokeDasharray="2 2" />
            </svg>

            {/* Render Nodes */}
            {nodes.map((node) => {
              const isSelected = selectedEntity.id === node.id;
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedEntity({
                    id: node.id,
                    name: node.name,
                    type: node.type,
                    riskScore: node.risk,
                    sharedIPs: node.risk > 80 ? 18 : 6,
                    connectedBrokers: node.risk > 80 ? 4 : 2,
                    recentVolume: node.risk > 80 ? '₹148.5 Crore' : '₹24.0 Crore',
                    flaggedReason: node.risk > 80 ? 'High sentiment velocity & synchronized IP order execution' : 'Standard institutional trade pattern'
                  })}
                  style={{ left: node.x, top: node.y }}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition duration-200 group ${
                    isSelected ? 'scale-110 z-20' : 'hover:scale-105 z-10'
                  }`}
                >
                  <div className={`p-3 rounded-2xl ${node.color} text-white shadow-lg flex items-center gap-2 border-2 ${
                    isSelected ? 'border-[#a9f0e0] ring-4 ring-[#206a5e]/30' : 'border-slate-900'
                  }`}>
                    <span className="material-symbols-outlined text-sm">hub</span>
                    <div className="text-left font-mono">
                      <p className="text-[11px] font-bold leading-none">{node.name}</p>
                      <p className="text-[9px] opacity-80 mt-0.5">{node.type}</p>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Canvas Overlay Legend */}
            <div className="absolute bottom-3 left-3 px-3 py-2 rounded-xl theme-surface-card border theme-border text-[10px] font-mono theme-text-muted space-y-1">
              <p className="font-bold theme-text">EDGE TYPES:</p>
              <p className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-red-500 inline-block"></span> Synchronized Order Flow</p>
              <p className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-[#206a5e] inline-block"></span> Social Hype Trigger</p>
              <p className="flex items-center gap-1.5"><span className="w-3 h-0.5 bg-purple-500 inline-block"></span> Shared IP Cluster</p>
            </div>

          </div>

        </div>

        {/* Right 4 Columns: Node Inspector & XAI Evidence Card */}
        <div className="lg:col-span-4 space-y-6">
          <div className="relative overflow-hidden theme-surface p-6 rounded-3xl border theme-border space-y-4 alpine-shadow group">
            <ClippedCircle circleSize={320} circleClassName="bg-[#206a5e]/20" />
            <div className="flex items-center justify-between border-b theme-border pb-3">
              <h3 className="text-base font-bold theme-text font-sans">Entity Inspector</h3>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#a9f0e0] text-[#095c51] font-bold">
                {selectedEntity.id}
              </span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div>
                <p className="theme-text-muted text-[10px]">Entity Name</p>
                <p className="font-bold theme-text text-sm font-sans">{selectedEntity.name}</p>
              </div>

              <div>
                <p className="theme-text-muted text-[10px]">Entity Category</p>
                <p className="text-[#206a5e] font-bold">{selectedEntity.type}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-2.5 rounded-xl theme-surface-low border theme-border">
                  <p className="theme-text-muted text-[9px]">Calculated Risk</p>
                  <p className="text-red-500 font-bold text-sm">{selectedEntity.riskScore} / 100</p>
                </div>
                <div className="p-2.5 rounded-xl theme-surface-low border theme-border">
                  <p className="theme-text-muted text-[9px]">Linked IP Hash</p>
                  <p className="text-amber-600 font-bold text-sm">{selectedEntity.sharedIPs} Accounts</p>
                </div>
              </div>

              <div>
                <p className="theme-text-muted text-[10px]">24h Trading Volume</p>
                <p className="font-bold theme-text">{selectedEntity.recentVolume}</p>
              </div>

              <div className="p-3 rounded-xl theme-surface-low border theme-border text-[11px] theme-text leading-relaxed">
                <span className="text-[#206a5e] font-bold">XAI TRIGGER REASON: </span>
                {selectedEntity.flaggedReason}
              </div>

              <button
                onClick={() => alert(`Generated evidence dossier for ${selectedEntity.name}`)}
                className="w-full py-2.5 rounded-xl bg-[#206a5e] text-white font-bold text-xs shadow hover:opacity-95 transition"
              >
                Compile Case Dossier
              </button>

            </div>

          </div>
        </div>

      </div>

    </div>
  );
}

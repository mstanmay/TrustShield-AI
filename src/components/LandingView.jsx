import React from 'react';
import { TextReveal } from '@/components/unlumen-ui/primitives/text-reveal';

export default function LandingView({ setActiveTab }) {
  return (
    <div className="space-y-0 relative z-10">
      
      {/* Hero Section */}
      <section className="relative min-h-[85vh] flex items-center pt-8 pb-16 overflow-hidden">
        
        {/* Hero Content Container */}
        <div className="max-w-7xl mx-auto px-6 relative z-10 grid lg:grid-cols-2 gap-12 items-center w-full">
          
          {/* Left Text Column */}
          <div className="space-y-6 max-w-2xl">
            
            {/* Pill Badge with Subtitle */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#cde8e1] text-[#3e5651] rounded-full border border-[#a9b4b1]/30 shadow-sm">
              <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: '"FILL" 1' }}>
                shield
              </span>
              <span className="font-data-mono text-xs font-bold tracking-wider uppercase">
                AI-POWERED FINANCIAL TRUST & FRAUD INTELLIGENCE PLATFORM
              </span>
            </div>

            {/* Headline - ONLY THIS HEADLINE IS WHITE IN COLOR */}
            <h2 className="font-display-lg text-4xl sm:text-6xl leading-[1.1] text-white font-bold tracking-tight">
              Defending Financial Trust with <span className="text-white italic font-normal">TrustShield AI</span>
            </h2>

            {/* Sub-headline Description */}
            <p className="font-body-lg text-base sm:text-lg max-w-xl text-[#0b2b23] dark:text-[#e3eae7] font-medium leading-relaxed bg-white/75 dark:bg-black/45 backdrop-blur-md p-4 rounded-2xl border border-white/60 dark:border-white/10 shadow-sm">
              An editorial-grade financial trust and fraud intelligence platform engineered for market oversight. TrustShield AI synthesizes multimodal data streams into actionable truth, ensuring capital integrity through autonomous vigilance.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-4 pt-4">
              <button 
                onClick={() => setActiveTab('investigations')}
                className="bg-[#206a5e] text-white px-8 py-4 rounded-xl font-display-lg font-bold flex items-center gap-3 hover:opacity-95 hover:shadow-lg transition-all active:scale-[0.98] cursor-pointer shadow-md"
              >
                <span>Initialize Investigation</span>
                <span className="material-symbols-outlined">arrow_forward</span>
              </button>

              <button 
                onClick={() => setActiveTab('threat_intel')}
                className="border border-[#206a5e] text-[#206a5e] bg-[#206a5e]/10 hover:bg-[#206a5e]/20 px-8 py-4 rounded-xl font-display-lg font-bold transition-all cursor-pointer"
              >
                View Technical Docs
              </button>
            </div>

          </div>

          {/* Right Floating Card Widget (Live Nexus Feed) */}
          <div className="hidden lg:block relative">
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-[#206a5e]/10 blur-3xl rounded-full"></div>
            
            <div className="theme-surface-card backdrop-blur-md p-6 rounded-3xl border theme-border alpine-shadow float-anim space-y-4">
              
              {/* Card Header */}
              <div className="flex justify-between items-center border-b theme-border pb-3">
                <span className="font-display-lg text-lg font-bold text-[#206a5e]">Live Nexus Feed</span>
                <span className="flex items-center gap-2 font-data-mono text-xs text-[#095c51] bg-[#a9f0e0] px-2.5 py-1 rounded font-bold">
                  <span className="w-2 h-2 rounded-full bg-[#095c51] animate-pulse"></span>
                  ACTIVE
                </span>
              </div>

              {/* Feed Items */}
              <div className="space-y-3 font-mono text-xs">
                
                <div className="p-3 theme-surface-high rounded-xl border theme-border flex items-start gap-4 hover:border-[#206a5e] transition cursor-pointer" onClick={() => setActiveTab('threat_intel')}>
                  <div className="w-10 h-10 rounded-lg bg-[#b7eaff] flex items-center justify-center text-[#235869] shrink-0">
                    <span className="material-symbols-outlined">videocam</span>
                  </div>
                  <div>
                    <p className="font-body-sm font-bold theme-text text-sm">Volatility Pattern Detected</p>
                    <p className="font-data-mono text-[11px] theme-text-muted mt-0.5">NODE: TRUST-SHIELD-01 | 0.04s latency</p>
                  </div>
                </div>

                <div className="p-3 theme-surface-high rounded-xl border theme-border flex items-start gap-4 hover:border-[#206a5e] transition cursor-pointer" onClick={() => setActiveTab('analysis_nexus')}>
                  <div className="w-10 h-10 rounded-lg bg-[#cde8e1] flex items-center justify-center text-[#3e5651] shrink-0">
                    <span className="material-symbols-outlined">description</span>
                  </div>
                  <div>
                    <p className="font-body-sm font-bold theme-text text-sm">Unusual Filings Analysis</p>
                    <p className="font-data-mono text-[11px] theme-text-muted mt-0.5">AGENT: TRUST-SENTINEL-04 | SAGE-SCORE: 88</p>
                  </div>
                </div>

                {/* Health Index Bar */}
                <div className="p-3 bg-[#206a5e] text-white rounded-xl flex items-center justify-between font-data-mono shadow">
                  <span className="font-bold tracking-wider text-xs">FINANCIAL TRUST INDEX</span>
                  <span className="font-bold text-sm">98.42%</span>
                </div>

              </div>

            </div>
          </div>

        </div>

      </section>

      {/* Multimodal Detection Section */}
      <section className="py-20 theme-surface rounded-3xl border theme-border my-8">
        <div className="max-w-7xl mx-auto px-6">
          
          <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
            <TextReveal
              text="Multimodal Detection"
              as="h3"
              splitBy="words"
              staggerDelay={0.05}
              duration={0.5}
              className="font-display-lg text-3xl sm:text-4xl text-[#206a5e] font-bold"
            />
            <TextReveal
              text="Our proprietary neural fabric deciphers patterns across disparate financial data types, creating a unified view of fraud activity."
              as="p"
              splitBy="words"
              staggerDelay={0.02}
              duration={0.4}
              className="font-body-lg theme-text-muted text-base sm:text-lg"
            />
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            
            {/* Card 1: Video */}
            <div 
              onClick={() => setActiveTab('threat_intel')}
              className="theme-surface-card p-8 rounded-3xl border theme-border hover:border-[#206a5e] transition-all group alpine-shadow cursor-pointer space-y-4"
            >
              <div className="w-14 h-14 theme-surface-high rounded-2xl flex items-center justify-center group-hover:bg-[#a9f0e0] transition-colors">
                <span className="material-symbols-outlined text-[#206a5e] text-3xl">play_circle</span>
              </div>
              <h4 className="font-display-lg text-xl font-bold theme-text">Video Synthesis</h4>
              <p className="font-body-sm text-sm theme-text-muted leading-relaxed">
                Real-time analysis of broadcast news, analyst streams, and visual sentiment to identify coordinated manipulation campaigns.
              </p>
              <div className="h-2 w-full theme-surface-high rounded-full overflow-hidden">
                <div className="h-full bg-[#206a5e] w-2/3"></div>
              </div>
              <div className="flex justify-between font-data-mono text-xs theme-text-muted pt-1">
                <span>LATENCY</span>
                <span className="font-bold text-[#206a5e]">0.002ms</span>
              </div>
            </div>

            {/* Card 2: Audio */}
            <div 
              onClick={() => setActiveTab('analysis_nexus')}
              className="theme-surface-card p-8 rounded-3xl border theme-border hover:border-[#206a5e] transition-all group alpine-shadow cursor-pointer space-y-4"
            >
              <div className="w-14 h-14 theme-surface-high rounded-2xl flex items-center justify-center group-hover:bg-[#a9f0e0] transition-colors">
                <span className="material-symbols-outlined text-[#206a5e] text-3xl">record_voice_over</span>
              </div>
              <h4 className="font-display-lg text-xl font-bold theme-text">Acoustic Forensics</h4>
              <p className="font-body-sm text-sm theme-text-muted leading-relaxed">
                Processing of investor calls and voice data using deep-learning to detect tonal stress indicators and linguistic anomalies.
              </p>
              <div className="h-2 w-full theme-surface-high rounded-full overflow-hidden">
                <div className="h-full bg-[#4b645e] w-1/2"></div>
              </div>
              <div className="flex justify-between font-data-mono text-xs theme-text-muted pt-1">
                <span>ACCURACY</span>
                <span className="font-bold text-[#206a5e]">94.2%</span>
              </div>
            </div>

            {/* Card 3: Document */}
            <div 
              onClick={() => setActiveTab('investigations')}
              className="theme-surface-card p-8 rounded-3xl border theme-border hover:border-[#206a5e] transition-all group alpine-shadow cursor-pointer space-y-4"
            >
              <div className="w-14 h-14 theme-surface-high rounded-2xl flex items-center justify-center group-hover:bg-[#a9f0e0] transition-colors">
                <span className="material-symbols-outlined text-[#206a5e] text-3xl">find_in_page</span>
              </div>
              <h4 className="font-display-lg text-xl font-bold theme-text">Semantic Document Scan</h4>
              <p className="font-body-sm text-sm theme-text-muted leading-relaxed">
                Cross-referencing millions of filings and legal documents to find hidden beneficial ownership structures and illicit connections.
              </p>
              <div className="h-2 w-full theme-surface-high rounded-full overflow-hidden">
                <div className="h-full bg-[#326677] w-4/5"></div>
              </div>
              <div className="flex justify-between font-data-mono text-xs theme-text-muted pt-1">
                <span>CAPACITY</span>
                <span className="font-bold text-[#206a5e]">1.2TB/s</span>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* Live Threat Intelligence Section */}
      <section className="py-20 theme-surface-low rounded-3xl border theme-border overflow-hidden my-8">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            
            <div className="space-y-6">
              <span className="font-data-mono text-xs font-bold text-[#206a5e] tracking-widest uppercase">
                REAL-TIME OVERSIGHT
              </span>
              <TextReveal
                text="Live Threat Intelligence"
                as="h3"
                splitBy="words"
                staggerDelay={0.05}
                duration={0.5}
                className="font-display-lg text-4xl theme-text font-bold block"
              />
              <TextReveal
                text="Our global sensor network monitors the entire financial ecosystem. Using autonomous agents, we identify threats before they impact retail stability."
                as="p"
                splitBy="words"
                staggerDelay={0.02}
                duration={0.4}
                className="font-body-lg theme-text-muted text-base leading-relaxed block"
              />

              <ul className="space-y-4 pt-2 font-body-sm text-sm theme-text">
                <li className="flex items-center gap-4">
                  <span className="w-8 h-8 rounded-full bg-[#a9f0e0] flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[#095c51] text-sm">check</span>
                  </span>
                  <span>Proactive Spoofing & Fraud Detection</span>
                </li>
                <li className="flex items-center gap-4">
                  <span className="w-8 h-8 rounded-full bg-[#a9f0e0] flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[#095c51] text-sm">check</span>
                  </span>
                  <span>Anomalous Trade & Transaction Aggregation</span>
                </li>
                <li className="flex items-center gap-4">
                  <span className="w-8 h-8 rounded-full bg-[#a9f0e0] flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[#095c51] text-sm">check</span>
                  </span>
                  <span>Social Sentiment Manipulation Alerts</span>
                </li>
              </ul>

              <button
                onClick={() => setActiveTab('threat_intel')}
                className="mt-4 bg-[#206a5e] text-white px-6 py-3 rounded-xl font-data-mono text-xs font-bold hover:opacity-90 transition cursor-pointer shadow"
              >
                Launch Surveillance Monitor →
              </button>
            </div>

            {/* India Map Surveillance Overlay graphic */}
            <div className="relative theme-surface-card rounded-[40px] p-2 overflow-hidden shadow-2xl border-4 theme-border">
              <div 
                className="w-full h-105 bg-cover bg-center rounded-4xl brightness-90 relative" 
                style={{ 
                  backgroundImage: `url("https://lh3.googleusercontent.com/aida-public/AB6AXuBVPx1DTKy3MigzLgM3PZWT23NkSmCVKmHq8f58W3iAJKnh9VDO3j6Kg2kULACKpxcV88jW2-G2zDxc7Y6OrU-4GEQiFoK-8OxTvk7RdAaDsYJqwxSKhWSjc2iqzZYi_Q4GSI-e55k8N9yc7_KCBK0ShvfLdlmUaPWyXhr8vye30WCxd26-_-1zdVTWy5-ZgP3fP-U4Eo8SpS90A-cjKrv9Gb26t3LctgJVuzO6cNkb6ClMerbZeaEbAPq5Yl_YCrL0oWoxl2NZl84")` 
                }}
              >
                <div className="absolute inset-0 p-6 flex flex-col justify-between">
                  <div className="flex justify-between items-start">
                    <div className="bg-[#0a0f0e]/80 backdrop-blur-md p-3.5 rounded-2xl border border-white/10 font-data-mono text-xs">
                      <div className="text-[#a9f0e0] font-bold">NODE: TRUST_SHIELD_01</div>
                      <div className="w-32 h-1 bg-white/20 mt-2 rounded-full overflow-hidden">
                        <div className="h-full bg-[#206a5e] w-3/4"></div>
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <div className="bg-[#206a5e] p-4 rounded-2xl text-white shadow-xl font-data-mono">
                      <div className="text-[10px] opacity-80 uppercase tracking-widest">ACTIVE THREATS</div>
                      <div className="font-display-lg text-2xl font-bold">02 Detected</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Automated Regulatory Reporting */}
      <section className="py-20 theme-surface rounded-3xl border theme-border my-8">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="theme-surface-card p-8 sm:p-12 rounded-4xl border theme-border alpine-shadow space-y-6">
            
            <div className="inline-block px-4 py-1.5 bg-[#cde8e1] text-[#3e5651] rounded-full font-data-mono text-xs font-bold">
              COMPLIANCE AUTOMATION
            </div>

            <h3 className="font-display-lg text-3xl sm:text-4xl text-[#206a5e] font-bold">
              Automated Regulatory Reporting
            </h3>

            <p className="font-body-lg theme-text-muted text-base leading-relaxed max-w-2xl mx-auto">
              Transition from months of manual auditing to seconds of autonomous generation. TrustShield AI drafts comprehensive, evidence-backed regulatory reports.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left pt-4">
              <div className="space-y-1.5">
                <span className="font-data-mono text-[#206a5e] font-bold text-xs">01. DATA INGEST</span>
                <p className="font-body-sm text-sm theme-text-muted">Aggregates multi-source evidence including logs, trade data, and communications.</p>
              </div>
              <div className="space-y-1.5">
                <span className="font-data-mono text-[#206a5e] font-bold text-xs">02. NARRATIVE GEN</span>
                <p className="font-body-sm text-sm theme-text-muted">Constructs an editorial-grade investigative narrative explaining the 'Why'.</p>
              </div>
              <div className="space-y-1.5">
                <span className="font-data-mono text-[#206a5e] font-bold text-xs">03. FILING-READY</span>
                <p className="font-body-sm text-sm theme-text-muted">Exports directly into compliant formats for official regulatory filing.</p>
              </div>
            </div>

            <button 
              onClick={() => setActiveTab('investigations')}
              className="mt-6 bg-[#4b645e] text-white px-8 py-4 rounded-full font-display-lg font-bold hover:bg-[#3e5651] transition-all flex items-center gap-3 mx-auto cursor-pointer shadow"
            >
              <span>Request Integration Portal</span>
              <span className="material-symbols-outlined">launch</span>
            </button>

          </div>
        </div>
      </section>

    </div>
  );
}

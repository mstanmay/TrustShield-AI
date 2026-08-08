import React, { useState } from 'react';
import { TextReveal } from '@/components/unlumen-ui/primitives/text-reveal';
import { 
  Search, 
  AlertTriangle, 
  Cpu, 
  Zap, 
  ShieldAlert, 
  Sliders, 
  BarChart2, 
  CheckCircle, 
  RefreshCw, 
  GitCommit, 
  Users, 
  ArrowRight,
  TrendingUp,
  Download
} from 'lucide-react';

export default function FraudDetectionView({ setActiveTab }) {
  const [selectedSecurity, setSelectedSecurity] = useState('XYZTECH (NSE)');
  const [socialVelocity, setSocialVelocity] = useState(84);
  const [orderCancellation, setOrderCancellation] = useState(89);
  const [blockRatio, setBlockRatio] = useState(4.8);
  const [sharedIpCount, setSharedIpCount] = useState(18);
  
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);

  const algorithms = [
    {
      id: 'pump_dump',
      name: 'Pump & Dump Sentinel',
      badge: 'SOCIAL + ORDER BOOK',
      desc: 'Correlates Telegram/WhatsApp hype velocity with sudden retail order placement spikes to detect artificial price inflation.',
      riskLevel: 'HIGH SENSITIVITY'
    },
    {
      id: 'insider_radar',
      name: 'Insider Trading Radar',
      badge: 'PRE-ANNOUNCEMENT BLOCK',
      desc: 'Monitors corporate action schedules against off-market block deal transfers by connected promoter entities.',
      riskLevel: 'MAX SURVEILLANCE'
    },
    {
      id: 'circular_trading',
      name: 'Circular Trading Loop Matcher',
      badge: 'WASH TRADE GRAPH',
      desc: 'Detects multi-broker synchronized trade loops operating with zero change in ultimate beneficial ownership (UBO).',
      riskLevel: 'GRAPH GRAPH MATCH'
    },
    {
      id: 'front_running',
      name: 'HFT Front-Running Scanner',
      badge: 'SUB-MILLISECOND ORDER',
      desc: 'Identifies high-frequency order placements strategically preceding large institutional block trade execution.',
      riskLevel: 'LATENCY 1ms'
    }
  ];

  const handleRunScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      const calculatedRisk = Math.round((socialVelocity * 0.35) + (orderCancellation * 0.25) + (blockRatio * 8) + (sharedIpCount * 1.2));

      const isCritical = calculatedRisk > 80;
      const isHigh = calculatedRisk > 60 && calculatedRisk <= 80;

      setScanResult({
        security: selectedSecurity,
        riskScore: calculatedRisk,
        severity: isCritical ? 'CRITICAL RISK' : isHigh ? 'HIGH RISK' : 'MODERATE RISK',
        shapFactors: [
          { feature: 'Social Media Velocity (Telegram/X Hype)', impact: `+${Math.round(socialVelocity * 0.45)}%`, value: `${socialVelocity}% above baseline` },
          { feature: 'Shared IP Hash Across Demat Accounts', impact: `+${Math.round(sharedIpCount * 1.5)}%`, value: `${sharedIpCount} linked accounts` },
          { feature: 'Order Cancellation Rate (Depth-5)', impact: `+${Math.round(orderCancellation * 0.2)}%`, value: `${orderCancellation}% cancellation` },
          { feature: 'Pre-announcement Block Ratio', impact: `+${Math.round(blockRatio * 4)}%`, value: `${blockRatio}x 30-day average` }
        ],
        diagnosis: isCritical 
          ? 'High confidence signal of orchestrated Pump & Dump scheme with coordinated Telegram group tipping and shared IP trading hubs.'
          : 'Suspicious order cancellation activity detected. Further monitoring advised on connected broker accounts.'
      });

      setIsScanning(false);
    }, 800);
  };

  return (
    <div className="space-y-8 pb-16">
      
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Search className="w-5 h-5 text-amber-400" />
            <TextReveal
              text="Autonomous Fraud Detection Engine"
              as="h2"
              splitBy="words"
              staggerDelay={0.04}
              duration={0.4}
              className="text-2xl font-bold text-white font-sans tracking-tight"
            />
            <span className="px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-mono font-bold border border-amber-500/30">
              AI SIMULATOR
            </span>
          </div>
          <TextReveal
            text="Test custom market signals or execute real-time detection routines on any Indian security."
            as="p"
            splitBy="words"
            staggerDelay={0.02}
            duration={0.3}
            className="text-xs text-slate-400 font-mono mt-1 block"
          />
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setActiveTab('analysis_nexus')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-950/40 border border-purple-500/40 text-purple-300 text-xs font-semibold hover:bg-purple-900/50 transition"
          >
            <GitCommit className="w-3.5 h-3.5" />
            <span>Open Entity Graph</span>
          </button>
        </div>
      </div>

      {/* Algorithms Showcase Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {algorithms.map((algo) => (
          <div key={algo.id} className="glass-panel p-5 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {algo.badge}
              </span>
              <span className="text-[10px] font-mono text-emerald-400 font-bold">{algo.riskLevel}</span>
            </div>
            <h3 className="font-bold text-white text-base font-sans">{algo.name}</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans">{algo.desc}</p>
          </div>
        ))}
      </div>

      {/* Interactive Fraud Detection Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left 6 Columns: Interactive Parameters Form */}
        <div className="lg:col-span-6 glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2 font-bold text-white text-base font-sans">
              <Sliders className="w-4 h-4 text-[#00f2fe]" />
              <span>Fraud Detection Parameter Controls</span>
            </div>
            <span className="text-xs font-mono text-slate-400">SEBI SURV-2026</span>
          </div>

          {/* Security Symbol Select */}
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-300">Target Security / Scrip Code</label>
            <select
              value={selectedSecurity}
              onChange={(e) => setSelectedSecurity(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-white focus:outline-none focus:border-[#00f2fe]"
            >
              <option value="XYZTECH (NSE)">NSE: XYZTECH (High Alert Candidate)</option>
              <option value="ADANIENT (NSE)">NSE: ADANIENT (Adani Enterprises)</option>
              <option value="TATAMOTORS (NSE)">NSE: TATAMOTORS (Tata Motors)</option>
              <option value="RELIANCE (NSE)">NSE: RELIANCE (Reliance Industries)</option>
              <option value="HDFCBANK (NSE)">NSE: HDFCBANK (HDFC Bank)</option>
              <option value="CUSTOM_NSE">CUSTOM_SECURITY_QUERY</option>
            </select>
          </div>

          {/* Slider 1: Social Media Hype Velocity */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">Social Hype Velocity (Telegram/X)</span>
              <span className="text-[#00f2fe] font-bold">{socialVelocity}% Above Baseline</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={socialVelocity}
              onChange={(e) => setSocialVelocity(Number(e.target.value))}
              className="w-full accent-[#00f2fe] cursor-pointer"
            />
          </div>

          {/* Slider 2: Order Cancellation Rate */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">Order Cancellation Rate (Depth-5)</span>
              <span className="text-amber-400 font-bold">{orderCancellation}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={orderCancellation}
              onChange={(e) => setOrderCancellation(Number(e.target.value))}
              className="w-full accent-amber-400 cursor-pointer"
            />
          </div>

          {/* Slider 3: Pre-Announcement Block Ratio */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">Pre-Announcement Block Deal Ratio</span>
              <span className="text-purple-400 font-bold">{blockRatio}x Average</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="0.1"
              value={blockRatio}
              onChange={(e) => setBlockRatio(Number(e.target.value))}
              className="w-full accent-purple-400 cursor-pointer"
            />
          </div>

          {/* Slider 4: Linked IP Demat Accounts */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-300">Linked Demat Accounts via Shared IP</span>
              <span className="text-red-400 font-bold">{sharedIpCount} Accounts</span>
            </div>
            <input
              type="range"
              min="1"
              max="50"
              value={sharedIpCount}
              onChange={(e) => setSharedIpCount(Number(e.target.value))}
              className="w-full accent-red-400 cursor-pointer"
            />
          </div>

          {/* Action Trigger Button */}
          <button
            onClick={handleRunScan}
            disabled={isScanning}
            className="w-full py-3.5 rounded-xl bg-linear-to-r from-amber-500 via-orange-500 to-[#00f2fe] text-slate-950 font-extrabold text-sm transition shadow-lg shadow-amber-500/20 flex items-center justify-center gap-2 hover:opacity-95"
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                <span>Running AI Neural Scan...</span>
              </>
            ) : (
              <>
                <Cpu className="w-4 h-4 text-slate-950" />
                <span>Execute Fraud Detection Neural Routine</span>
              </>
            )}
          </button>
        </div>

        {/* Right 6 Columns: Scan Results & XAI SHAP Breakdown */}
        <div className="lg:col-span-6 space-y-6">
          
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 min-h-105 flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-[#00f2fe]" />
                <h3 className="text-base font-bold text-white font-sans">AI Diagnostic & XAI Report</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">ENGINE: SENTINEL-NN-V4</span>
            </div>

            {!scanResult && !isScanning && (
              <div className="flex flex-col items-center justify-center text-center py-16 space-y-3">
                <Cpu className="w-12 h-12 text-slate-600" />
                <p className="text-slate-400 text-xs font-mono">Adjust the parameter sliders on the left and click "Execute Neural Routine" to generate a real-time XAI Fraud Diagnosis.</p>
              </div>
            )}

            {isScanning && (
              <div className="flex flex-col items-center justify-center text-center py-16 space-y-4">
                <RefreshCw className="w-10 h-10 text-[#00f2fe] animate-spin" />
                <p className="text-slate-300 text-xs font-mono animate-pulse">Scanning NSE order books, Telegram social logs & depository records...</p>
              </div>
            )}

            {scanResult && !isScanning && (
              <div className="space-y-5">
                
                {/* Result Header Card */}
                <div className={`p-4 rounded-xl border flex items-center justify-between ${
                  scanResult.riskScore > 80 
                    ? 'bg-red-950/30 border-red-500/50' 
                    : 'bg-amber-950/30 border-amber-500/50'
                }`}>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400">TARGET: {scanResult.security}</span>
                    <h4 className="text-xl font-extrabold text-white font-mono mt-0.5">{scanResult.severity}</h4>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-extrabold font-mono text-[#00f2fe]">{scanResult.riskScore}</span>
                    <span className="text-xs font-mono text-slate-400"> / 100</span>
                  </div>
                </div>

                {/* XAI SHAP Attribution Bars */}
                <div className="space-y-3">
                  <h5 className="text-xs font-mono text-slate-300 font-bold uppercase tracking-wider">
                    Explainable AI (SHAP) Feature Attribution:
                  </h5>
                  {scanResult.shapFactors.map((factor, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-slate-300 text-[11px]">{factor.feature}</span>
                        <span className="text-[#00f2fe] font-bold">{factor.impact}</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                        <div 
                          className="h-full bg-linear-to-r from-[#0052cc] to-[#00f2fe] rounded-full" 
                          style={{ width: `${Math.min(100, parseInt(factor.impact) * 2)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Diagnosis Text */}
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed">
                  <span className="text-emerald-400 font-bold">NEURAL SUMMARY: </span>
                  {scanResult.diagnosis}
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-3 pt-2">
                  <button 
                    onClick={() => setActiveTab('analysis_nexus')}
                    className="flex-1 py-2.5 rounded-xl bg-linear-to-r from-[#0052cc] to-[#00f2fe] text-white font-bold text-xs shadow-md shadow-[#0052cc]/30 hover:opacity-95 transition flex items-center justify-center gap-1.5"
                  >
                    <span>Inspect Entity Graph</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <button 
                    onClick={() => alert(`Dossier for ${scanResult.security} generated and prepared for SEBI Enforcement export.`)}
                    className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs font-semibold hover:border-slate-600 transition flex items-center gap-1.5"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export PDF</span>
                  </button>
                </div>

              </div>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}

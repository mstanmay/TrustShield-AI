import React from 'react';
import { TextReveal } from '@/components/unlumen-ui/primitives/text-reveal';
import { 
  BarChart3, 
  ShieldCheck, 
  AlertCircle, 
  FileText, 
  TrendingUp, 
  Building2, 
  Users, 
  Lock, 
  Download, 
  CheckCircle,
  Clock
} from 'lucide-react';

export default function ExecutiveBoardView() {
  const enforcementActions = [
    { id: 'SCN-2026-94', target: 'M/s Apex Capital FPI', action: 'Show Cause Notice & Trading Freeze', date: '23 Jul 2026', status: 'NOTICE ISSUED' },
    { id: 'SCN-2026-93', target: 'Telegram Channel "Bulls_Hub" Admin', action: 'SEBI Section 11B Restraint Order', date: '22 Jul 2026', status: 'DEBARRED' },
    { id: 'SCN-2026-92', target: 'M/s Zenith Broking Ltd', action: 'Disgorgement of ₹42.8 Crore Illicit Gains', date: '20 Jul 2026', status: 'IMPOSED' },
    { id: 'SCN-2026-91', target: 'Promoter Group Entities (XYZTECH)', action: 'Demat Account Freezing', date: '18 Jul 2026', status: 'FROZEN' }
  ];

  return (
    <div className="space-y-8 pb-16">
      
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <TextReveal
              text="Executive Surveillance Board Overview"
              as="h2"
              splitBy="words"
              staggerDelay={0.04}
              duration={0.4}
              className="text-2xl font-bold text-white font-sans tracking-tight"
            />
            <span className="px-2.5 py-0.5 rounded bg-blue-500/20 text-blue-300 text-[10px] font-mono font-bold border border-blue-500/30">
              BOARD AUDIT
            </span>
          </div>
          <TextReveal
            text="High-level executive metrics for SEBI Chairman & Surveillance Committee Members."
            as="p"
            splitBy="words"
            staggerDelay={0.02}
            duration={0.3}
            className="text-xs text-slate-400 font-mono mt-1 block"
          />
        </div>

        <button 
          onClick={() => alert('Generating Board Executive Summary PDF...')}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-linear-to-r from-[#0052cc] to-[#00f2fe] text-white text-xs font-bold transition shadow-md shadow-[#0052cc]/20"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Board PDF</span>
        </button>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
          <p className="text-xs text-slate-400 font-mono">Enforcement Orders Issued (Q3)</p>
          <h3 className="text-3xl font-extrabold text-white font-mono">142 Orders</h3>
          <p className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
            <CheckCircle className="w-3.5 h-3.5" /> 100% Legal Adjudication Compliance
          </p>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
          <p className="text-xs text-slate-400 font-mono">Disgorgement & Fines Imposed</p>
          <h3 className="text-3xl font-extrabold text-[#00f2fe] font-mono">₹284.2 Crore</h3>
          <p className="text-[11px] text-slate-400 font-mono">Deposited into Investor Protection Fund</p>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2">
          <p className="text-xs text-slate-400 font-mono">Active Market Intermediaries Monitored</p>
          <h3 className="text-3xl font-extrabold text-purple-400 font-mono">1,840 Entities</h3>
          <p className="text-[11px] text-purple-300 font-mono">Stock Brokers, FPIs, R&T Agents, Depositories</p>
        </div>
      </div>

      {/* Enforcement Actions Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-base font-bold text-white font-sans">Recent SEBI Enforcement Actions & Restraint Orders</h3>
          <span className="text-xs font-mono text-slate-400">JULY 2026 AUDIT LOG</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] text-slate-400 uppercase">
                <th className="pb-3">Notice ID</th>
                <th className="pb-3">Target Intermediary / Entity</th>
                <th className="pb-3">Enforcement Action Taken</th>
                <th className="pb-3">Date</th>
                <th className="pb-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {enforcementActions.map((act) => (
                <tr key={act.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 font-bold text-[#00f2fe]">{act.id}</td>
                  <td className="py-3.5 font-bold text-white font-sans">{act.target}</td>
                  <td className="py-3.5 text-slate-300 font-sans">{act.action}</td>
                  <td className="py-3.5 text-slate-400">{act.date}</td>
                  <td className="py-3.5 text-right">
                    <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-bold border border-red-500/40 text-[10px]">
                      {act.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}

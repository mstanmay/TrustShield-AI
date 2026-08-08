import React from 'react';
import Logo from './Logo';

export default function Footer({ setActiveTab }) {
  return (
    <footer className="theme-surface-high theme-text-muted py-16 border-t theme-border font-sans text-xs transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-12">
          
          {/* Logo & Info */}
          <div className="col-span-1 md:col-span-2 space-y-6">
            <Logo onClick={() => setActiveTab('home')} showSubtitle={false} />
            <p className="font-body-sm max-w-sm theme-text-muted text-sm leading-relaxed">
              AI-Powered Financial Trust & Fraud Intelligence Platform. Advancing the technological frontier of financial market oversight.
            </p>
          </div>

          {/* Resources */}
          <div>
            <h5 className="font-data-mono text-xs font-bold text-[#206a5e] tracking-widest mb-6">RESOURCES</h5>
            <ul className="space-y-4 font-body-sm theme-text-muted">
              <li>
                <button onClick={() => setActiveTab('threat_intel')} className="hover:text-[#206a5e] transition">
                  API Documentation
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('analysis_nexus')} className="hover:text-[#206a5e] transition">
                  Regulatory Framework
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('investigations')} className="hover:text-[#206a5e] transition">
                  Incident Reports
                </button>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h5 className="font-data-mono text-xs font-bold text-[#206a5e] tracking-widest mb-6">CONTACT</h5>
            <ul className="space-y-4 font-body-sm theme-text-muted">
              <li>
                <button onClick={() => setActiveTab('threat_intel')} className="hover:text-[#206a5e] transition">
                  Security Desk
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('home')} className="hover:text-[#206a5e] transition">
                  System Status
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('investigations')} className="hover:text-[#206a5e] transition">
                  Press &amp; Inquiries
                </button>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom copyright */}
        <div className="mt-16 pt-8 border-t theme-border flex flex-col md:flex-row justify-between items-center gap-6 font-data-mono text-[11px] theme-text-muted">
          <p>© 2026 TRUSTSHIELD AI | ALL RIGHTS RESERVED | CONFIDENTIAL SYSTEM</p>
          <div className="flex gap-6">
            <span className="material-symbols-outlined theme-text-muted cursor-pointer hover:text-[#206a5e]">language</span>
            <span className="material-symbols-outlined theme-text-muted cursor-pointer hover:text-[#206a5e]">rss_feed</span>
            <span className="material-symbols-outlined theme-text-muted cursor-pointer hover:text-[#206a5e]">shield_with_house</span>
          </div>
        </div>

      </div>
    </footer>
  );
}

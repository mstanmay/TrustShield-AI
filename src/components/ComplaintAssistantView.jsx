import React, { useState } from 'react';
import { TextReveal } from '@/components/unlumen-ui/primitives/text-reveal';

export default function ComplaintAssistantView() {
  const [activeStep, setActiveStep] = useState(1);
  const [category, setCategory] = useState('Broker Misconduct & Unauthorized Trading');
  const [entityName, setEntityName] = useState('');
  const [panNumber, setPanNumber] = useState('');
  const [description, setDescription] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const [ticketResult, setTicketResult] = useState(null);
  const [trackId, setTrackId] = useState('TRUST/MH26/0091823');
  const [trackedStatus, setTrackedStatus] = useState(null);

  const handleFileUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedFile(e.target.files[0].name);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    const newTicketId = `TRUST/MH26/${Math.floor(100000 + Math.random() * 900000)}`;
    setTicketResult({
      ticketId: newTicketId,
      status: 'AI Triage Complete - Assigned to Regulatory Officer',
      sla: '2.4 Days',
      assignedZone: 'TrustShield AI Central Regional Hub',
      severity: 'HIGH SEVERITY',
      extractedData: {
        category,
        entity: entityName || 'Apex Securities Ltd',
        pan: panNumber || 'ABCDE1234F',
        confidenceScore: '98.4%'
      }
    });
    setActiveStep(4);
  };

  const handleTrackSubmit = (e) => {
    e.preventDefault();
    setTrackedStatus({
      id: trackId,
      status: 'UNDER ACTIVE INVESTIGATION',
      category: 'Unauthorized Options Trading & Demat Debit',
      filingDate: '21 July 2026',
      assignedOfficer: 'Dr. R. K. Sharma (Deputy Director, Market Regulation)',
      timeline: [
        { date: '21 Jul 2026, 10:14 AM', step: 'Grievance Registered via TrustShield AI Portal' },
        { date: '21 Jul 2026, 10:15 AM', step: 'AI NLP Document Parser extracted Contract Note & Bank Statement' },
        { date: '22 Jul 2026, 02:30 PM', step: 'Intermediary Explanation Demanded (SLA: 48 hours)' },
        { date: '23 Jul 2026, 09:00 AM', step: 'Reconciliation under review by Compliance Officer' }
      ]
    });
  };

  return (
    <div className="space-y-8 py-8 relative z-10">
      
      {/* Top Banner */}
      <div className="theme-surface p-6 rounded-3xl border theme-border flex flex-wrap items-center justify-between gap-4 alpine-shadow">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[#206a5e] text-2xl">policy</span>
            <TextReveal
              text="TrustShield Grievance & Investigation Portal"
              as="h2"
              splitBy="words"
              staggerDelay={0.04}
              duration={0.4}
              className="font-display-lg text-2xl font-bold text-[#206a5e]"
            />
            <span className="font-data-mono text-xs px-2.5 py-0.5 rounded bg-[#a9f0e0] text-[#095c51] font-bold">
              SLA GUARANTEE
            </span>
          </div>
          <TextReveal
            text="Automated investor grievance filing, instant NLP document parsing & real-time ticket tracking."
            as="p"
            splitBy="words"
            staggerDelay={0.02}
            duration={0.3}
            className="font-body-sm text-xs theme-text-muted block"
          />
        </div>

        <div className="flex items-center gap-2 text-xs font-mono theme-text theme-surface-low px-3.5 py-2 rounded-xl border theme-border">
          <span className="material-symbols-outlined text-[#206a5e] text-sm">verified_user</span>
          <span>Helpline: 1800 266 7575</span>
        </div>
      </div>

      {/* Grid: Left 7 Columns Grievance Wizard / Right 5 Columns Complaint Tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left 7 Columns: Filing Wizard */}
        <div className="lg:col-span-7 space-y-6">
          <div className="theme-surface p-6 rounded-3xl border theme-border alpine-shadow space-y-6">
            
            {/* Step Stepper Header */}
            <div className="flex items-center justify-between border-b theme-border pb-4">
              {[
                { num: 1, label: 'Category' },
                { num: 2, label: 'Details' },
                { num: 3, label: 'Evidence' },
                { num: 4, label: 'Ticket' }
              ].map(s => (
                <div 
                  key={s.num}
                  onClick={() => s.num < activeStep && setActiveStep(s.num)}
                  className={`flex items-center gap-2 cursor-pointer font-mono text-xs ${
                    activeStep === s.num 
                      ? 'text-[#206a5e] font-bold' 
                      : activeStep > s.num 
                      ? 'text-emerald-600' 
                      : 'theme-text-muted'
                  }`}
                >
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                    activeStep === s.num ? 'bg-[#206a5e] text-white' : activeStep > s.num ? 'bg-[#a9f0e0] text-[#095c51] font-bold' : 'theme-surface-low'
                  }`}>
                    {s.num}
                  </span>
                  <span className="hidden sm:inline">{s.label}</span>
                </div>
              ))}
            </div>

            {/* Step 1: Category */}
            {activeStep === 1 && (
              <div className="space-y-4">
                <h3 className="font-display-lg text-lg font-bold theme-text">Select Grievance Category</h3>
                <div className="space-y-2">
                  {[
                    'Broker Misconduct & Unauthorized Trading',
                    'Demat Account Unauthorized Stock Debit',
                    'Non-Receipt of Dividend / IPO Allotment Refund',
                    'Social Media Pump & Dump Stock Loss',
                    'Mutual Fund NAV Calculation Discrepancy'
                  ].map(cat => (
                    <div
                      key={cat}
                      onClick={() => setCategory(cat)}
                      className={`p-3.5 rounded-xl border text-xs font-mono cursor-pointer transition flex items-center justify-between ${
                        category === cat
                          ? 'bg-[#206a5e]/15 border-[#206a5e] theme-text font-bold'
                          : 'theme-surface-card border-transparent theme-text-muted hover:border-slate-400'
                      }`}
                    >
                      <span>{cat}</span>
                      {category === cat && <span className="material-symbols-outlined text-[#206a5e] text-sm">check_circle</span>}
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => setActiveStep(2)}
                  className="w-full py-3.5 rounded-xl bg-[#206a5e] text-white font-bold text-xs shadow flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <span>Proceed to Entity Details</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
              </div>
            )}

            {/* Step 2: Details */}
            {activeStep === 2 && (
              <div className="space-y-4 font-mono text-xs">
                <h3 className="font-display-lg text-lg font-bold theme-text">Intermediary & PAN Information</h3>
                
                <div className="space-y-2">
                  <label className="theme-text">Name of Intermediary / Broker</label>
                  <input
                    type="text"
                    placeholder="e.g. Apex Securities Ltd"
                    value={entityName}
                    onChange={(e) => setEntityName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl theme-surface-low border theme-border theme-text focus:outline-none focus:border-[#206a5e]"
                  />
                </div>

                <div className="space-y-2">
                  <label className="theme-text">Investor PAN Number</label>
                  <input
                    type="text"
                    placeholder="ABCDE1234F"
                    value={panNumber}
                    onChange={(e) => setPanNumber(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl theme-surface-low border theme-border theme-text uppercase focus:outline-none focus:border-[#206a5e]"
                  />
                </div>

                <div className="space-y-2">
                  <label className="theme-text">Grievance Summary Description</label>
                  <textarea
                    rows={3}
                    placeholder="Describe the incident, date of transaction, and financial loss incurred..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl theme-surface-low border theme-border theme-text focus:outline-none focus:border-[#206a5e]"
                  ></textarea>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setActiveStep(1)}
                    className="w-1/3 py-3 rounded-xl theme-surface-low border theme-border theme-text font-bold text-xs"
                  >
                    Back
                  </button>
                  <button
                    onClick={() => setActiveStep(3)}
                    className="w-2/3 py-3 rounded-xl bg-[#206a5e] text-white font-bold text-xs shadow flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <span>Upload Evidence</span>
                    <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Evidence Upload */}
            {activeStep === 3 && (
              <form onSubmit={handleFormSubmit} className="space-y-4 font-mono text-xs">
                <h3 className="font-display-lg text-lg font-bold theme-text">AI Evidence Parsing & Upload</h3>
                
                <div className="border-2 border-dashed theme-border rounded-2xl p-8 text-center theme-surface-low space-y-3 transition">
                  <span className="material-symbols-outlined text-4xl text-[#206a5e]">cloud_upload</span>
                  <div>
                    <p className="theme-text font-bold">Drag & drop Contract Note / Bank Statement PDF</p>
                    <p className="theme-text-muted text-[11px] mt-1">TrustShield AI automatically parses dates, transaction hashes & amounts.</p>
                  </div>
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="evidence-upload"
                  />
                  <label
                    htmlFor="evidence-upload"
                    className="inline-block px-4 py-2 rounded-xl theme-surface-card border theme-border theme-text cursor-pointer hover:border-[#206a5e] transition"
                  >
                    {uploadedFile ? `Uploaded: ${uploadedFile}` : 'Browse Files'}
                  </label>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setActiveStep(2)}
                    className="w-1/3 py-3 rounded-xl theme-surface-low border theme-border theme-text font-bold text-xs"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="w-2/3 py-3 rounded-xl bg-[#206a5e] text-white font-bold text-xs shadow flex items-center justify-center gap-1.5 cursor-pointer"
                  >
                    <span>Submit Grievance Ticket</span>
                    <span className="material-symbols-outlined text-sm">arrow_forward</span>
                  </button>
                </div>
              </form>
            )}

            {/* Step 4: Submission Confirmation */}
            {activeStep === 4 && ticketResult && (
              <div className="space-y-4 font-mono text-xs">
                <div className="p-4 rounded-xl bg-[#a9f0e0]/20 border border-[#206a5e] space-y-2">
                  <div className="flex items-center gap-2 text-[#095c51] font-bold">
                    <span className="material-symbols-outlined text-lg">check_circle</span>
                    <span className="text-sm font-sans">Grievance Ticket Successfully Registered!</span>
                  </div>
                  <p className="theme-text">Registration Number: <span className="text-[#206a5e] font-bold">{ticketResult.ticketId}</span></p>
                  <p className="theme-text">Guaranteed SLA: <span className="text-emerald-600 font-bold">{ticketResult.sla}</span></p>
                </div>

                <div className="p-4 rounded-xl theme-surface-low border theme-border space-y-2 theme-text">
                  <p className="theme-text-muted text-[10px]">AI PARSED CONFIRMATION:</p>
                  <p>• Category: {ticketResult.extractedData.category}</p>
                  <p>• Intermediary: {ticketResult.extractedData.entity}</p>
                  <p>• PAN: {ticketResult.extractedData.pan}</p>
                  <p>• Assigned Hub: {ticketResult.assignedZone}</p>
                </div>

                <button
                  onClick={() => {
                    setActiveStep(1);
                    setTicketResult(null);
                  }}
                  className="w-full py-2.5 rounded-xl theme-surface-low border theme-border theme-text font-bold"
                >
                  Submit Another Grievance
                </button>
              </div>
            )}

          </div>
        </div>

        {/* Right 5 Columns: Real-Time Ticket Tracker */}
        <div className="lg:col-span-5 space-y-6">
          <div className="theme-surface p-6 rounded-3xl border theme-border alpine-shadow space-y-4">
            <div className="flex items-center justify-between border-b theme-border pb-3">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[#206a5e]">search</span>
                <h3 className="text-base font-bold theme-text font-sans">Ticket Tracker</h3>
              </div>
              <span className="text-xs font-mono theme-text-muted">SEARCH REGISTRATION</span>
            </div>

            <form onSubmit={handleTrackSubmit} className="space-y-3 font-mono text-xs">
              <label className="theme-text">Enter Registration Number</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={trackId}
                  onChange={(e) => setTrackId(e.target.value)}
                  placeholder="e.g. TRUST/MH26/0091823"
                  className="flex-1 px-3.5 py-2 rounded-xl theme-surface-low border theme-border theme-text focus:outline-none focus:border-[#206a5e]"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#206a5e] text-white font-bold cursor-pointer"
                >
                  Track
                </button>
              </div>
            </form>

            {trackedStatus && (
              <div className="space-y-4 pt-2 border-t theme-border font-mono text-xs">
                <div className="p-3.5 rounded-xl theme-surface-low border theme-border space-y-1">
                  <span className="text-[10px] theme-text-muted">REGISTRATION NO: {trackedStatus.id}</span>
                  <h4 className="text-sm font-bold text-[#206a5e] font-sans">{trackedStatus.status}</h4>
                  <p className="text-[11px] theme-text-muted">{trackedStatus.category}</p>
                </div>

                <div className="space-y-3 pl-2 border-l-2 border-[#206a5e]">
                  {trackedStatus.timeline.map((item, idx) => (
                    <div key={idx} className="relative pl-4">
                      <span className="absolute -left-5.25 top-1 w-2.5 h-2.5 rounded-full bg-[#206a5e]"></span>
                      <p className="text-[10px] theme-text-muted">{item.date}</p>
                      <p className="theme-text font-medium">{item.step}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>

      </div>

    </div>
  );
}

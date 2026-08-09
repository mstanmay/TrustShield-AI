import os
import base64
import json

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(DEMO_DIR, "screenshots")

slides_data = [
    {
        "filename": "01_landing_hero.png",
        "badge": "HOME",
        "tag": "CASE 1: PLATFORM OVERVIEW",
        "title": "TrustShield AI — Real-Time Financial Trust Platform",
        "desc": "Autonomous market oversight engine for Indian retail investors with live Financial Trust Index (98.42%) and active sentinel monitoring.",
        "duration": 4.0
    },
    {
        "filename": "02_landing_cta.png",
        "badge": "INVESTIGATION",
        "tag": "CASE 2: INVESTIGATION LAUNCH",
        "title": "Multi-Modal Ingestion & Investigation Entrypoint",
        "desc": "Direct access to AI forensic pipelines, multi-format upload dropzone, and regulatory intelligence verification.",
        "duration": 4.0
    },
    {
        "filename": "03_multimodal_detection.png",
        "badge": "CAPABILITIES",
        "tag": "CASE 3: MULTI-MODAL DETECTION",
        "title": "Acoustic, Video & Document Forensics Engine",
        "desc": "Video synthesis analysis (0.002ms latency), Voice cloning detection (94.2% accuracy), and Semantic OCR (1.2 TB/s capacity).",
        "duration": 4.5
    },
    {
        "filename": "04_feature_cards.png",
        "badge": "VIGILANCE",
        "tag": "CASE 4: SENTINEL VIGILANCE",
        "title": "Autonomous Scam & Sentiment Analysis",
        "desc": "Continuous monitoring of social hype groups, pump-and-dump channels, and spoofed circulars.",
        "duration": 4.0
    },
    {
        "filename": "05_threat_intelligence_section.png",
        "badge": "THREAT INTEL",
        "tag": "CASE 5: THREAT INTELLIGENCE",
        "title": "Live Sensor Network & National Fraud Heatmap",
        "desc": "Global sensor network monitoring with India-wide threat detection map showing active nodes and CERT-In advisories.",
        "duration": 4.5
    },
    {
        "filename": "06_analysis_nexus_graph.png",
        "badge": "ANALYSIS NEXUS",
        "tag": "CASE 6: FRAUD NETWORK GRAPH",
        "title": "Cross-Market Entity Graph & XAI Forensics",
        "desc": "Uncovering organized syndicates: Apex Capital FPI (Risk 88/100, 18 Accounts, Rs 148.5 Cr volume), Target Stock, and Promoter Shells.",
        "duration": 5.0
    },
    {
        "filename": "07_analysis_nexus_footer.png",
        "badge": "ANALYSIS NEXUS",
        "tag": "CASE 7: XAI FEATURE ATTRIBUTION",
        "title": "Automated Evidence Dossier Compilation",
        "desc": "Synchronized off-market order flow detection, social hype triggers, and shared IP cluster proofs.",
        "duration": 4.5
    },
    {
        "filename": "08_investigations_portal.png",
        "badge": "INVESTIGATIONS",
        "tag": "CASE 8: GRIEVANCE FILING",
        "title": "SEBI SCORES Grievance & Investigation Portal",
        "desc": "Structured 4-step investor redressal workflow with SLA guarantee, helpline 1800 266 7575, and live registration tracking.",
        "duration": 4.5
    },
    {
        "filename": "09_grievance_wizard.png",
        "badge": "INVESTIGATIONS",
        "tag": "CASE 9: COMPLAINT CATEGORIZATION",
        "title": "Specialized Incident Category Classifier",
        "desc": "Broker misconduct, unauthorized Demat debits, IPO refund defaults, and social media fraud cases.",
        "duration": 4.0
    },
    {
        "filename": "10_home_overview.png",
        "badge": "HOME",
        "tag": "CASE 10: COMPLETE ECOSYSTEM",
        "title": "Production-Ready Investor Protection Stack",
        "desc": "Unified React 19 Frontend + FastAPI Backend with end-to-end multi-agent orchestration and theme switching.",
        "duration": 4.0
    }
]

print("Reading and encoding screenshots into Base64...")
for item in slides_data:
    filepath = os.path.join(SCREENSHOTS_DIR, item["filename"])
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            item["data_uri"] = f"data:image/png;base64,{b64}"
            print(f"Encoded {item['filename']} ({len(item['data_uri']) // 1024} KB)")
    else:
        print(f"WARNING: Missing {filepath}")
        item["data_uri"] = ""

slides_json = json.dumps(slides_data)

# ── 1. Generate Self-Contained TrustShield_AI_Demo.html ───────────────────────
html_demo = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TrustShield AI — Self-Contained Platform Video Demo</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg-primary: #070c0a;
      --bg-card: rgba(14, 26, 21, 0.95);
      --accent: #22c55e;
      --accent-dim: #166534;
      --text-primary: #f0fdf4;
      --text-secondary: #86efac;
      --text-muted: #94a3b8;
      --border: rgba(34, 197, 94, 0.2);
    }}

    body {{
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
    }}

    /* ── Animated Background ────────────────────────────────────────── */
    .bg-grid {{
      position: fixed;
      inset: 0;
      background-image: 
        linear-gradient(rgba(34, 197, 94, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34, 197, 94, 0.04) 1px, transparent 1px);
      background-size: 50px 50px;
      z-index: 0;
      pointer-events: none;
    }}

    /* ── Header ─────────────────────────────────────────────────────── */
    header {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(7, 12, 10, 0.9);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .logo-icon {{
      width: 34px; height: 34px;
      background: linear-gradient(135deg, var(--accent), var(--accent-dim));
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 16px;
      color: #fff;
    }}
    .logo-text {{
      font-weight: 800;
      font-size: 17px;
      letter-spacing: -0.5px;
    }}
    .logo-text span {{ color: var(--accent); }}
    .header-badge {{
      background: rgba(34,197,94,0.12);
      color: var(--text-secondary);
      padding: 5px 14px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      border: 1px solid var(--border);
    }}

    .controls {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .controls button {{
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-primary);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 7px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      font-family: inherit;
    }}
    .controls button:hover {{
      background: rgba(34,197,94,0.2);
      border-color: var(--accent);
      color: var(--accent);
    }}
    .controls button.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}

    /* ── Main Container ─────────────────────────────────────────────── */
    .container {{
      position: relative;
      z-index: 1;
      max-width: 1160px;
      width: 100%;
      margin: 0 auto;
      padding: 30px 20px;
      flex: 1;
    }}

    /* ── Slideshow ───────────────────────────────────────────────────── */
    .slideshow-wrap {{
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--bg-card);
      box-shadow: 0 0 80px rgba(34,197,94,0.08), 0 20px 60px rgba(0,0,0,0.6);
    }}
    .slide-viewport {{
      position: relative;
      width: 100%;
      aspect-ratio: 16 / 10;
      overflow: hidden;
      background: #000;
    }}
    .slide {{
      position: absolute;
      inset: 0;
      opacity: 0;
      transition: opacity 0.7s ease-in-out;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .slide.active {{ opacity: 1; }}
    .slide img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: #050807;
    }}

    /* ── Caption Overlay ─────────────────────────────────────────────── */
    .slide-caption {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 36px 28px 20px;
      background: linear-gradient(transparent, rgba(5, 10, 8, 0.95) 40%, rgba(5, 10, 8, 0.98));
      border-top: 1px solid rgba(34, 197, 94, 0.15);
    }}
    .slide-caption .badge {{
      display: inline-block;
      background: var(--accent);
      color: #000;
      padding: 4px 12px;
      border-radius: 6px;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .slide-caption h3 {{
      font-size: 20px;
      font-weight: 700;
      margin-bottom: 4px;
      color: #fff;
    }}
    .slide-caption p {{
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
      max-width: 800px;
    }}

    /* ── Progress Bar ────────────────────────────────────────────────── */
    .progress-bar-container {{
      height: 4px;
      background: rgba(255,255,255,0.08);
      cursor: pointer;
    }}
    .progress-bar {{
      height: 100%;
      background: linear-gradient(90deg, var(--accent), #4ade80);
      width: 0%;
      transition: width 0.1s linear;
    }}

    /* ── Slide Indicators ────────────────────────────────────────────── */
    .slide-indicators {{
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 12px 20px;
      background: rgba(8, 14, 11, 0.9);
      border-top: 1px solid var(--border);
    }}
    .indicator {{
      flex: 1;
      height: 4px;
      border-radius: 2px;
      background: rgba(255,255,255,0.12);
      cursor: pointer;
      transition: background 0.3s;
      position: relative;
      overflow: hidden;
    }}
    .indicator.completed {{ background: var(--accent); }}
    .indicator.active {{ background: rgba(255,255,255,0.2); }}
    .indicator.active::after {{
      content: '';
      position: absolute;
      left: 0; top: 0; bottom: 0;
      background: var(--accent);
      animation: indicatorFill var(--anim-duration, 4.5s) linear forwards;
    }}
    @keyframes indicatorFill {{
      from {{ width: 0%; }}
      to {{ width: 100%; }}
    }}

    .slide-counter {{
      position: absolute;
      top: 14px;
      right: 18px;
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(8px);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      color: rgba(255,255,255,0.9);
      z-index: 10;
      border: 1px solid rgba(255,255,255,0.15);
    }}

    /* ── Chapter Buttons ─────────────────────────────────────────────── */
    .chapters-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      gap: 10px;
      margin-top: 24px;
    }}
    .chapter-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px 14px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .chapter-card:hover {{
      border-color: var(--accent);
      background: rgba(34, 197, 94, 0.08);
      transform: translateY(-2px);
    }}
    .chapter-card.active {{
      border-color: var(--accent);
      background: rgba(34, 197, 94, 0.15);
    }}
    .chapter-card .c-tag {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 2px;
    }}
    .chapter-card .c-title {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-primary);
      line-height: 1.3;
    }}

    footer {{
      text-align: center;
      padding: 24px;
      color: var(--text-muted);
      font-size: 12px;
      border-top: 1px solid var(--border);
      margin-top: auto;
    }}
  </style>
</head>
<body>

  <div class="bg-grid"></div>

  <header>
    <div class="logo">
      <div class="logo-icon">🛡️</div>
      <div class="logo-text">Trust<span>Shield</span> AI</div>
    </div>
    <div class="header-badge">SEBI TechSprint 2026 · Standalone Demo</div>
    <div class="controls">
      <button id="prevBtn" onclick="prevSlide()">← Prev</button>
      <button id="playBtn" class="active" onclick="togglePlay()">⏸ Pause</button>
      <button id="nextBtn" onclick="nextSlide()">Next →</button>
    </div>
  </header>

  <div class="container">

    <div class="slideshow-wrap">
      <div class="progress-bar-container" onclick="seekProgressBar(event)">
        <div class="progress-bar" id="progressBar"></div>
      </div>

      <div class="slide-viewport" id="slideViewport">
        <div class="slide-counter" id="slideCounter">1 / 10</div>
      </div>

      <div class="slide-indicators" id="indicators"></div>
    </div>

    <!-- Chapter Grid -->
    <div class="chapters-grid" id="chaptersGrid"></div>

  </div>

  <footer>
    © 2026 TrustShield AI · Built for SEBI TechSprint 2026 · Standalone Offline Demo
  </footer>

  <script>
    const slides = {slides_json};

    let currentSlide = 0;
    let isPlaying = true;
    let timer = null;
    const DURATION = 4500;

    const viewport = document.getElementById('slideViewport');
    const indicators = document.getElementById('indicators');
    const progressBar = document.getElementById('progressBar');
    const counter = document.getElementById('slideCounter');
    const playBtn = document.getElementById('playBtn');
    const chaptersGrid = document.getElementById('chaptersGrid');

    // Build Slides & Chapters
    slides.forEach((s, i) => {{
      const div = document.createElement('div');
      div.className = `slide ${{i === 0 ? 'active' : ''}}`;
      div.innerHTML = `
        <img src="${{s.data_uri}}" alt="${{s.title}}">
        <div class="slide-caption">
          <div class="badge">${{s.badge}}</div>
          <h3>${{s.title}}</h3>
          <p>${{s.desc}}</p>
        </div>
      `;
      viewport.appendChild(div);

      const ind = document.createElement('div');
      ind.className = `indicator ${{i === 0 ? 'active' : ''}}`;
      ind.style.setProperty('--anim-duration', DURATION + 'ms');
      ind.onclick = () => goToSlide(i);
      indicators.appendChild(ind);

      const card = document.createElement('div');
      card.className = `chapter-card ${{i === 0 ? 'active' : ''}}`;
      card.id = `card-${{i}}`;
      card.onclick = () => goToSlide(i);
      card.innerHTML = `
        <div class="c-tag">${{s.tag.split(':')[0]}}</div>
        <div class="c-title">${{s.title.split('—')[0]}}</div>
      `;
      chaptersGrid.appendChild(card);
    }});

    function goToSlide(index) {{
      const slideEls = document.querySelectorAll('.slide');
      const indEls = document.querySelectorAll('.indicator');
      const cardEls = document.querySelectorAll('.chapter-card');

      slideEls[currentSlide].classList.remove('active');
      indEls[currentSlide].classList.remove('active', 'completed');
      cardEls[currentSlide].classList.remove('active');

      for (let j = 0; j < index; j++) {{
        indEls[j].classList.add('completed');
        indEls[j].classList.remove('active');
      }}
      for (let j = index; j < slides.length; j++) {{
        indEls[j].classList.remove('completed');
      }}

      currentSlide = index;
      slideEls[currentSlide].classList.add('active');
      indEls[currentSlide].classList.add('active');
      cardEls[currentSlide].classList.add('active');

      counter.textContent = `${{currentSlide + 1}} / ${{slides.length}}`;
      progressBar.style.width = `${{((currentSlide + 1) / slides.length) * 100}}%`;

      if (isPlaying) startTimer();
    }}

    function nextSlide() {{
      goToSlide((currentSlide + 1) % slides.length);
    }}

    function prevSlide() {{
      goToSlide((currentSlide - 1 + slides.length) % slides.length);
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      playBtn.textContent = isPlaying ? '⏸ Pause' : '▶ Play';
      playBtn.classList.toggle('active', isPlaying);
      if (isPlaying) {{
        startTimer();
      }} else {{
        clearTimeout(timer);
      }}
    }}

    function startTimer() {{
      clearTimeout(timer);
      timer = setTimeout(() => {{
        nextSlide();
      }}, DURATION);
    }}

    function seekProgressBar(e) {{
      const rect = e.currentTarget.getBoundingClientRect();
      const pct = (e.clientX - rect.left) / rect.width;
      const targetIdx = Math.min(slides.length - 1, Math.max(0, Math.floor(pct * slides.length)));
      goToSlide(targetIdx);
    }}

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); nextSlide(); }}
      if (e.key === 'ArrowLeft') {{ e.preventDefault(); prevSlide(); }}
      if (e.key === 'p' || e.key === 'P') {{ togglePlay(); }}
    }});

    // Start auto-play
    startTimer();
  </script>
</body>
</html>
"""

output_path_demo = os.path.join(DEMO_DIR, "TrustShield_AI_Demo.html")
with open(output_path_demo, "w", encoding="utf-8") as f:
    f.write(html_demo)
print(f"Generated standalone demo at: {output_path_demo} ({os.path.getsize(output_path_demo) // 1024} KB)")

# Also update demo/index.html to use Base64 embedded images so it never breaks on download
with open(os.path.join(DEMO_DIR, "index.html"), "r", encoding="utf-8") as f:
    idx_content = f.read()

# Replace the chapters array with Base64 embedded data
old_chapters_token = "const chapters = ["
new_chapters_code = f"const chapters = {slides_json};\n    // Process base64\n    chapters.forEach(c => c.file = c.data_uri);"

if old_chapters_token in idx_content:
    # Find start and end of chapters array in index.html
    start_pos = idx_content.find("const chapters = [")
    end_pos = idx_content.find("];\n\n    // Compute start times", start_pos)
    if end_pos != -1:
        updated_idx = idx_content[:start_pos] + f"const chapters = {slides_json};\n    chapters.forEach(c => {{ c.file = c.data_uri; }});" + idx_content[end_pos + 2:]
        with open(os.path.join(DEMO_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(updated_idx)
        print("Updated demo/index.html with Base64 assets as well!")

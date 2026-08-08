# 🚀 Cloud Deployment Guide: Vercel (Frontend) & Render (Backend)

This guide provides end-to-end instructions for deploying the **TrustShield AI** platform across **Vercel** (for the React 19 + Vite frontend) and **Render** (for the FastAPI backend).

---

## 🏗️ Architecture Overview in Cloud

```
┌────────────────────────────────────────────────────────┐
│                   Vercel Edge Network                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │   TrustShield AI React 19 Frontend               │  │
│  │   https://trustshield-ai.vercel.app              │  │
│  └────────────────────────┬─────────────────────────┘  │
└───────────────────────────┼────────────────────────────┘
                            │ HTTPS API Calls
                            │ (VITE_API_URL)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Render Cloud Platform                │
│  ┌──────────────────────────────────────────────────┐  │
│  │   TrustShield AI FastAPI Web Service             │  │
│  │   https://trustshield-backend.onrender.com       │  │
│  │   - Multi-Modal AI Decision Engine               │  │
│  │   - SEBI Regulatory RAG Pipeline                 │  │
│  │   - Fraud Intelligence & Complaint Assistant     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## ⚡ Part 1: Deploy Backend on Render

Render will host the **FastAPI REST API**. You can deploy it either using **Docker** (recommended) or **Python 3.11 Native**.

### Method A: 1-Click Render Blueprint (Recommended)

1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository: `https://github.com/mstanmay/TrustShield-AI`.
4. Render will automatically detect the root `render.yaml` configuration.
5. Click **Apply**. Render will automatically build the container and start the web service.

---

### Method B: Manual Web Service Setup on Render

1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Web Service**.
2. Connect the `TrustShield-AI` repository.
3. Configure the following settings:
   - **Name**: `trustshield-backend`
   - **Region**: `Oregon (US West)` or `Frankfurt (EU Central)`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker` (or `Python 3`)
     - If using **Docker**:
       - Docker Command: *leave blank (handled by Dockerfile)*
     - If using **Python 3**:
       - Build Command: `pip install -r requirements.txt`
       - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

4. Add **Environment Variables** in the Render Dashboard:

| Variable | Recommended Value | Description |
|---|---|---|
| `PORT` | `8000` | Port injected by Render |
| `DEBUG` | `false` | Disable debug logs in production |
| `LOG_LEVEL` | `INFO` | Structured JSON log level |
| `JWT_SECRET_KEY` | *(Click "Generate" or enter 32+ random hex characters)* | Secret key for JWT auth tokens |
| `DATABASE_URL` | `sqlite+aiosqlite:///./sebi_fraud.db` | Auto-fallback SQLite DB (or your Render PostgreSQL URL) |
| `DATABASE_SYNC_URL` | `sqlite:///./sebi_fraud.db` | Sync SQLite URL (or sync PostgreSQL URL) |
| `ANTHROPIC_API_KEY` | *(Optional - your Claude API key)* | Required for full LLM reasoning chains |
| `ENABLE_MALWARE_SCAN` | `false` | Toggle offline/online scanners |
| `ENABLE_VIRUSTOTAL` | `false` | VirusTotal threat intelligence toggle |
| `OTEL_ENABLED` | `false` | OpenTelemetry tracing toggle |

5. Click **Deploy Web Service**.
6. Once deployment finishes, copy your backend URL (e.g. `https://trustshield-backend.onrender.com`).
7. Test the health endpoint by visiting: `https://trustshield-backend.onrender.com/health` (should return `{"status":"healthy"}`).

---

## 🌐 Part 2: Deploy Frontend on Vercel

Vercel will host the optimized **React 19 single-page application**.

### Step-by-Step Vercel Deployment

1. Log in to [Vercel](https://vercel.com/).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository: `mstanmay/TrustShield-AI`.
4. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `./`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
5. Expand **Environment Variables** and add:

| Name | Value | Note |
|---|---|---|
| `VITE_API_URL` | `https://trustshield-backend.onrender.com` | **Your Render backend URL from Part 1** |

6. Click **Deploy**.
7. Vercel will build the frontend assets in ~30 seconds and assign a live URL (e.g. `https://trustshield-ai.vercel.app`).

---

## 🔄 Part 3: Testing & Verification

Once both frontend and backend are deployed:

1. **Open Frontend**: Navigate to your Vercel URL `https://your-project.vercel.app`.
2. **Test Ingestion**: Go to the **Multi-Modal Investigation Workspace** and upload a sample file, URL, or WhatsApp text snippet.
3. **Check Live Pipeline**: View the **Analysis Nexus** to confirm parallel agent verdicts (Deepfake, Voice, Document OCR, Phishing URL) and weighted risk assessment.
4. **Generate SEBI Complaint**: Test draft creation and PDF preview in the **Complaint Assistant**.
5. **Explore Threat Intel**: Check the live threat ticker and CERT-In advisory feeds.

---

## 🛠️ Troubleshooting & Tips

- **Render Free Tier Spin-Down**: Free instances on Render spin down after 15 minutes of inactivity and take ~30-50 seconds to cold start on the first request. The frontend has built-in retry handling.
- **CORS Errors**: The FastAPI backend is configured with wildcard CORS (`allow_origins=["*"]`) enabled out-of-the-box, ensuring seamless cross-origin communication from your Vercel domain.
- **Custom Domains**: You can attach custom domains on both Vercel (e.g., `trustshield.yourdomain.com`) and Render without re-deploying.

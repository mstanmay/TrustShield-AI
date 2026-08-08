# TrustShield AI - SEBI Financial Trust and Fraud Intelligence Platform

A production-grade, multi-modal fraud and scam detection platform built to protect investors from SEBI-related scams — fake advisors, deepfakes, cloned voice calls, forged circulars, phishing links, QR codes, and messaging scams.

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────────┐
│  Ingestion   │     │        LangGraph Orchestrator (STEP 2)          │
│  API (v1)    │────▶│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  POST/ingest │     │  │Deepfake  │  │ Voice    │  │ Document     │  │
└─────────────┘     │  │Agent 3a  │  │Agent 3b  │  │ Agent 3c     │  │
       │            │  └────┬─────┘  └────┬─────┘  └──────┬───────┘  │
       │ Celery     │       │             │               │           │
       │ async      │  ┌────┴─────┐       │         ┌─────┴────────┐  │
       ▼            │  │Phishing  │       │         │              │  │
  ┌─────────┐       │  │Agent 3d  ├───────┴─────────┤  Join Node   │  │
  │ Case DB │       │  └──────────┘                  └──────┬──────┘  │
  │ Postgres│       │                                       │         │
  └─────────┘       │  ┌──────────────────┐  ┌──────────────▼──────┐  │
                    │  │ Risk Assessment  │  │  Decision Engine    │  │
                    │  │ Agent 3e         │──│  (STEP 4)           │  │
                    │  └──────────────────┘  └─────────────────────┘  │
                    └──────────────────────────────────────────────────┘
                              │                          │
                    ┌─────────▼──────┐          ┌────────▼─────────┐
                    │ Dashboard APIs │          │ Complaint        │
                    │ (STEP 5)       │          │ Assistant (STEP 6│
                    └────────────────┘          └──────────────────┘
```

## Tech Stack

| Component | Technology |
|---|---|
| Framework | Python 3.11+ / FastAPI (async) |
| Orchestration | LangGraph (StateGraph with parallel fan-out) |
| LLM | Anthropic Claude (configurable model via env var) |
| Task Queue | Celery + Redis |
| Database | PostgreSQL + pgvector |
| Object Storage | S3-compatible (MinIO for local dev) |
| Auth | JWT (python-jose + passlib) |
| Containerization | Docker + docker-compose |
| Observability | structlog (JSON) + OpenTelemetry tracing |
| Frontend Integration | React 19 (Vite + TailwindCSS) mounted at `/` |

## 🎨 Frontend Application Integration

The backend mounts the compiled React 19 SPA (`/dist`) at the root URL `/`, serving both the interactive user interface and REST APIs on a single unified port (`http://localhost:8000`).

### View Component Architecture

| View Component | File Location | Functional Role |
|---|---|---|
| **Landing Page** | `src/components/LandingView.jsx` | Hero banner, live threat ticker, platform stats |
| **Investigation Workspace** | `src/components/FraudDetectionView.jsx` | Multi-modal file dropzone, URL & text analysis |
| **Analysis Nexus** | `src/components/AnalysisNexusView.jsx` | Multi-agent verdict cards & LLM reasoning chain |
| **Threat Intelligence** | `src/components/ThreatIntelView.jsx` | Real-time CERT-In domain & AbuseIPDB IP scanner |
| **SCORES Assistant** | `src/components/ComplaintAssistantView.jsx` | SEBI SCORES complaint draft editor & PDF download |
| **Executive Board** | `src/components/ExecutiveBoardView.jsx` | Real-time Chart.js analytics & fraud trend heatmaps |

## Quick Start

### 1. Clone & Configure
```bash
cd backend
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY for LLM-powered explanations
# (optional: works without it using FallbackLLMProvider)
```

### 2. Run with Docker
```bash
docker-compose up --build
```

This starts 5 services:
- **API** — `http://localhost:8000` (FastAPI + Swagger at `/docs`)
- **Worker** — Celery worker processing analysis tasks
- **PostgreSQL** — `localhost:5432` (with pgvector extension)
- **Redis** — `localhost:6379`
- **MinIO** — `http://localhost:9000` (S3-compatible, console at `:9001`)

### 3. Run Tests
```bash
# All tests
docker-compose run --rm api pytest tests/ -v

# Specific agent
docker-compose run --rm api pytest tests/test_phishing_agent.py -v

# Integration test
docker-compose run --rm api pytest tests/test_integration_pipeline.py -v
```

### 4. Try It
```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "analyst", "email": "analyst@test.com", "password": "securepass123"}'

# Upload a file for analysis
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@suspicious_document.pdf"
# Returns: {"case_id": "...", "status": "pending"}

# Submit a URL for analysis
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "url=https://sebl.gov.in/login"

# Submit a WhatsApp message
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "text_content=URGENT: Guaranteed 100% returns!" \
  -F "input_type_hint=whatsapp_message"

# Check results
curl http://localhost:8000/api/v1/cases/{case_id}

# Generate complaint PDF
curl -X POST http://localhost:8000/api/v1/complaints/{case_id}/generate
```

## Architecture → Code Mapping

| Architecture Step | Code Location |
|---|---|
| **STEP 1 — Ingestion Layer** | `app/api/v1/ingest.py`, `app/core/file_detection.py`, `app/core/storage.py` |
| **STEP 2 — AI Orchestrator** | `app/orchestrator/graph.py`, `app/orchestrator/routing.py`, `app/orchestrator/state.py` |
| **STEP 3a — Deepfake Agent** | `app/agents/deepfake_agent.py`, `app/adapters/deepfake_model.py` |
| **STEP 3b — Voice Agent** | `app/agents/voice_agent.py` |
| **STEP 3c — Document Agent** | `app/agents/document_agent.py`, `app/adapters/ocr_provider.py` |
| **STEP 3d — Phishing Agent** | `app/agents/phishing_agent.py`, `app/adapters/reputation_provider.py` |
| **STEP 3e — Risk Assessment** | `app/agents/risk_assessment_agent.py`, `app/adapters/llm_provider.py` |
| **STEP 4 — Decision Engine** | `app/decision_engine/engine.py` |
| **STEP 5 — Dashboard APIs** | `app/api/v1/dashboard.py`, `app/api/v1/alerts.py`, `app/api/v1/cases.py` |
| **STEP 6 — Complaint Assistant** | `app/complaint_assistant/collector.py`, `app/complaint_assistant/generator.py`, `app/complaint_assistant/pdf_renderer.py`, `app/api/v1/complaints.py` |

## API Endpoints

### Ingestion
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/ingest` | Upload file/URL/text for analysis |

### Cases
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/cases/{case_id}` | Full case results + verdict |
| GET | `/api/v1/cases` | List cases (filterable) |

### Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/dashboard/threat-intel` | Aggregated threat statistics |
| GET | `/api/v1/dashboard/heatmap` | Geo/time fraud heatmap |
| GET | `/api/v1/dashboard/trends` | Emerging scam trend clusters |
| GET | `/api/v1/dashboard/alerts` | Browser protection alerts |
| WS | `/api/v1/dashboard/ws/alerts` | WebSocket for real-time alerts |
| POST | `/api/v1/dashboard/alerts/webhook` | Register webhook for alerts |
| POST | `/api/v1/dashboard/complaints/draft` | Complaint draft entry point |

### Complaints
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/complaints/{case_id}/generate` | Generate complaint draft |
| PATCH | `/api/v1/complaints/{case_id}` | Edit complaint draft |
| POST | `/api/v1/complaints/{case_id}/confirm` | Confirm and generate PDF |
| GET | `/api/v1/complaints/{case_id}/pdf` | Download complaint PDF |

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| POST | `/api/v1/auth/refresh` | Refresh access token |

## Swapping in Real Model Providers

### Deepfake Detection
Set `DEEPFAKE_ONNX_MODEL_PATH=/path/to/model.onnx` to use a trained classifier instead of the heuristic detector.

### LLM Provider
Set `ANTHROPIC_API_KEY=your_key` and optionally `ANTHROPIC_MODEL_NAME=claude-sonnet-4-20250514`.

### Threat Intelligence
Set `ENABLE_VIRUSTOTAL=true` and `VIRUSTOTAL_API_KEY=your_key` for real domain reputation checking.

### Malware Scanning
Set `ENABLE_MALWARE_SCAN=true` and ensure ClamAV daemon is running.

### OCR
Default: Tesseract (requires `tesseract-ocr` system package). Cloud OCR: extend `CloudOCRProvider` in `app/adapters/ocr_provider.py`.

## Agent Output Standard

Every agent returns:
```json
{
  "agent_type": "deepfake",
  "result": "Human-readable summary",
  "confidence_score": 0.75,
  "evidence": [
    {
      "finding": "What was found",
      "severity": "critical",
      "detail": {"score": 0.8}
    }
  ],
  "raw_model_output": {"full_raw_data": "..."},
  "execution_time_ms": 1234.5,
  "error": null
}
```

## Decision Engine Reasoning

The Decision Engine shows its full reasoning chain:
```json
{
  "classification": "Fraudulent",
  "risk_score": 0.82,
  "threat_severity": "Critical",
  "explanation": "LLM-generated explanation grounded in agent evidence...",
  "evidence_breakdown": {
    "deepfake": {"weight": 0.30, "raw_confidence": 0.45, "weighted_score": 0.135},
    "phishing": {"weight": 0.25, "raw_confidence": 0.95, "weighted_score": 0.237}
  },
  "reasoning_chain": [
    "Risk score 0.820 >= 0.65 → FRAUDULENT",
    "Agent 'deepfake': confidence=0.450 × weight=0.300 = contribution=0.135",
    "Agent 'phishing': confidence=0.950 × weight=0.250 = contribution=0.237"
  ]
}
```

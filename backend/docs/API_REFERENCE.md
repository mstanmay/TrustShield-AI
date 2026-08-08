# SEBI AI Trust Platform — API Reference Manual

Base URL: `http://localhost:8000/api/v1`

---

## 1. Case Ingestion & Analysis
- **POST `/ingest`**: Upload video, audio, image, PDF, URL, or WhatsApp text. Returns `case_id`.
- **GET `/cases/{case_id}`**: Fetch detailed case analysis results & breakdown.
- **GET `/cases`**: List all submitted cases with status filtering.

## 2. Dashboard Analytics
- **GET `/dashboard/stats`**: Executive board summary metrics (Total Scams, Protected Capital, Active Threats).
- **GET `/dashboard/complaints/draft`**: Auto-generate SEBI SCORES complaint body.

## 3. Threat Intelligence
- **GET `/threat-intel/domain?domain=sebl.gov.in`**: Whois age, VirusTotal score, CERT-In blacklist.
- **GET `/threat-intel/ip?ip_address=185.220.101.5`**: AbuseIPDB score, ISP, TOR exit node status.
- **GET `/threat-intel/file-hash?file_hash=...`**: VirusTotal malware engine scan results.

## 4. Browser Extension Services
- **POST `/extension/scan-url`**: Fast sub-100ms URL phishing & typosquatting check.
- **POST `/extension/scan-text`**: Fast text snippet scam keyword scan.
- **POST `/extension/scan-dom`**: DOM structural inspection for SEBI logo impersonation.
- **GET `/extension/active-threats`**: Live active threat feed for badge count.

## 5. Fraud Intelligence Graph
- **GET `/graph/case?case_id=CASE-001`**: Case entity relationship subgraph.
- **GET `/graph/entity?entity_id=ENT-9012`**: K-hop neighborhood graph around an entity.
- **GET `/graph/network`**: Full cross-case fraud intelligence network graph.
- **GET `/graph/communities`**: Louvain scam campaign clusters.

## 6. MLOps & Model Dashboard
- **GET `/models/dashboard`**: Aggregated MLOps performance metrics (Precision, Recall, F1, ROC).
- **GET `/models/registry`**: List of registered production ML model versions.

## 7. Regulatory RAG Knowledge Base
- **POST `/knowledge/index`**: Re-index SEBI regulatory circulars.
- **GET `/knowledge/search`**: Hybrid BM25 + Vector semantic search across regulatory knowledge.

## 8. Observability & Metrics
- **GET `/metrics`**: Standard Prometheus exposition metrics format.

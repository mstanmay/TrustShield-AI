# End-to-End Execution Flow

## Case Ingestion & Asynchronous Pipeline Workflow

```
[User Upload / Extension Scan]
         │
         ▼
[FastAPI Gateway :8000] ── (Rate Limiting & OWASP Headers)
         │
         ├─► Save Metadata to PostgreSQL
         ├─► Upload Artifact to MinIO S3
         │
         ▼
[RabbitMQ Event Bus] ──► Publish `case.uploaded` Event
         │
         ▼
[Celery Task Worker]
         │
         ▼
[LangGraph Orchestrator] (Parallel Agent Execution)
         ├──► Deepfake Video Agent (Landmark jitter & temporal consistency)
         ├──► Voice Cloning Agent (Spectral flatness & pitch contour)
         ├──► Document Verification Agent (Tesseract OCR & SEBI format check)
         └──► Phishing URL Agent (Whois age, typosquatting & reputation)
         │
         ▼
[RAG & Knowledge Retrieval] ── (Qdrant Vector DB :6333)
         │
         ▼
[Risk Assessment Engine] ── (Claude 4.6 Thinking / Rule Engine)
         │
         ├─► Persist Graph Entities in Neo4j (:7474)
         ├─► Log Model Inference Metrics to MLflow (:5000)
         ├─► Record Metric Counters in Prometheus (:9090)
         │
         ▼
[Notification & Web Dashboard] ── (WebSocket Push & SEBI SCORES Complaint Draft)
```

---

## Processing Timings & SLAs

- **Browser Extension Real-Time Scan**: `< 100 ms` (Redis LRU cached fast-path)
- **Multi-Modal Deepfake & Voice Analysis**: `< 2.5 seconds`
- **RAG Knowledge Context Retrieval**: `< 45 ms`
- **Neo4j Graph Traversal**: `< 30 ms`
- **Full Async Pipeline End-to-End**: `< 4.0 seconds`

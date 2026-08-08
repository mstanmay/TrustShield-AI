# MLOps Production Model Catalog

| Model Name | Version | Stage | Precision | Recall | F1 Score | ROC AUC | Latency (ms) | Description |
|---|---|---|---|---|---|---|---|---|
| **DeepfakeDetectionModel** | `v1.2.0` | Production | 0.942 | 0.915 | 0.928 | 0.965 | 145 ms | Landmark jitter & facial temporal artifact classifier |
| **VoiceCloningDetector** | `v1.1.0` | Production | 0.925 | 0.890 | 0.907 | 0.948 | 95 ms | F0 contour & spectral flatness audio fingerprint model |
| **DocumentVerificationOCR** | `v2.0.1` | Production | 0.968 | 0.952 | 0.960 | 0.981 | 320 ms | Tesseract OCR & SEBI circular format validator |
| **PhishingURLScanner** | `v1.5.0` | Production | 0.985 | 0.970 | 0.977 | 0.992 | 45 ms | Levenshtein typosquatting & reputation scoring model |
| **RiskAssessmentLLM** | `v4.6.0` | Production | 0.935 | 0.920 | 0.927 | 0.955 | 850 ms | Anthropic Claude 4.6 Thinking + RAG reasoning engine |

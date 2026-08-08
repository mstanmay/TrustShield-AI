# Enterprise Deployment Runbook

## Prerequisites
- Docker Engine 24.0+ & Docker Compose v2.20+
- Python 3.11+ (for local CLI / test execution)

## Quick Start (Single Command Launch)

1. Clone repository & enter backend folder:
   ```bash
   cd backend
   ```

2. Copy production environment configuration:
   ```bash
   cp .env.production.example .env
   ```

3. Launch full 14-container ecosystem:
   ```bash
   docker compose up -d --build
   ```

4. Verify service health status:
   ```bash
   docker compose ps
   ```

---

## Service Endpoints & Management Consoles

- **Unified Web Application**: `http://localhost:8000`
- **FastAPI OpenAPI Swagger**: `http://localhost:8000/docs`
- **Grafana Analytics Dashboards**: `http://localhost:3000` (User: `admin`, Pass: `sebi_grafana_secret`)
- **Jaeger Distributed Tracing UI**: `http://localhost:16686`
- **Prometheus Metrics Engine**: `http://localhost:9090`
- **RabbitMQ Management Dashboard**: `http://localhost:15672` (User: `guest`, Pass: `guest`)
- **Neo4j Graph Database Browser**: `http://localhost:7474` (User: `neo4j`, Pass: `sebi_graph_secret`)
- **MLflow Model Registry**: `http://localhost:5000`
- **MinIO Object Storage Console**: `http://localhost:9001`

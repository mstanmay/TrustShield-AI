"""
Unit tests for Phase 12 Enterprise Docker Compose — YAML syntax, 14 service declarations, network tiering, and volumes.
"""

from __future__ import annotations

from pathlib import Path
import pytest
import yaml

BACKEND_DIR = Path(__file__).parent.parent


class TestEnterpriseDockerCompose:
    """Unit test suite for Enterprise Docker Compose configuration."""

    def test_docker_compose_yaml_validity(self):
        compose_file = BACKEND_DIR / "docker-compose.yml"
        assert compose_file.exists()

        with open(compose_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "services" in data
        services = data["services"]

        expected_services = [
            "api", "worker", "postgres", "redis", "minio",
            "qdrant", "mlflow", "rabbitmq", "neo4j", "prometheus",
            "grafana", "jaeger", "loki", "promtail"
        ]

        for sname in expected_services:
            assert sname in services, f"Missing service container: {sname}"

    def test_docker_compose_network_segmentation(self):
        compose_file = BACKEND_DIR / "docker-compose.yml"
        with open(compose_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "networks" in data
        networks = data["networks"]
        assert "sebi-frontend-net" in networks
        assert "sebi-backend-net" in networks
        assert "sebi-data-net" in networks

    def test_docker_compose_persistent_volumes(self):
        compose_file = BACKEND_DIR / "docker-compose.yml"
        with open(compose_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "volumes" in data
        volumes = data["volumes"]
        expected_volumes = [
            "pgdata", "redisdata", "miniodata", "qdrantdata", "mlflowdata",
            "rabbitmqdata", "neo4jdata", "prometheusdata", "grafanadata", "lokidata"
        ]
        for vname in expected_volumes:
            assert vname in volumes, f"Missing persistent volume: {vname}"

    def test_docker_compose_prod_override(self):
        prod_file = BACKEND_DIR / "docker-compose.prod.yml"
        assert prod_file.exists()

        with open(prod_file, "r", encoding="utf-8") as f:
            pdata = yaml.safe_load(f)

        assert "services" in pdata
        assert "deploy" in pdata["services"]["api"]
        assert "resources" in pdata["services"]["api"]["deploy"]

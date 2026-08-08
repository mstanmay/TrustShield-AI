"""
Unit tests for Phase 9 Grafana Dashboards & Provisioning — datasources and dashboard JSON validations.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import yaml

GRAFANA_DIR = Path(__file__).parent.parent / "grafana"


class TestGrafanaDashboards:
    """Unit test suite for Grafana datasource and dashboard provisioning configurations."""

    def test_prometheus_datasource_config(self):
        ds_file = GRAFANA_DIR / "datasources" / "prometheus.yml"
        assert ds_file.exists()

        with open(ds_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "datasources" in data
        ds = data["datasources"][0]
        assert ds["name"] == "Prometheus"
        assert ds["type"] == "prometheus"
        assert ds["url"] == "http://prometheus:9090"

    def test_dashboard_provider_config(self):
        provider_file = GRAFANA_DIR / "dashboards" / "dashboard_provider.yml"
        assert provider_file.exists()

        with open(provider_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "providers" in data
        p = data["providers"][0]
        assert p["name"] == "SEBI Trust Platform Dashboards"

    def test_dashboard_json_validity(self):
        dashboards = ["system_health.json", "agent_latency.json", "scam_trends.json", "model_accuracy.json"]

        for dname in dashboards:
            dfile = GRAFANA_DIR / "dashboards" / dname
            assert dfile.exists()

            with open(dfile, "r", encoding="utf-8") as f:
                djson = json.load(f)

            assert "title" in djson
            assert "panels" in djson
            assert len(djson["panels"]) >= 2

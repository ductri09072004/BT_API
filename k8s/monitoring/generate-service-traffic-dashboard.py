#!/usr/bin/env python3
"""
Generate a Grafana dashboard (service traffic/latency/error) from docker-compose services
using Prometheus client metrics exposed by each service.

Metrics used (per service name S):
  - S_http_requests_total{status,method,path}
  - S_http_request_duration_seconds_bucket

Outputs file: bt-api-service-traffic.json in this directory.
"""

import json
from pathlib import Path
import yaml


THIS_DIR = Path(__file__).parent
ROOT = (THIS_DIR / "../../").resolve()
OUTPUT = THIS_DIR / "bt-api-service-traffic.json"


def load_services_from_compose() -> list[str]:
    compose_path = ROOT / "docker-compose.yml"
    with compose_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    names: list[str] = []
    for name in (data.get("services", {}) or {}).keys():
        lower = name.lower()
        if any(x in lower for x in ["grafana", "prometheus", "loki", "monitor", "kibana", "elasticsearch"]):
            continue
        names.append(name)
    return names


def panel_stat(panel_id: int, title: str, expr: str, x: int, y: int, w: int = 6, h: int = 6) -> dict:
    return {
        "id": panel_id,
        "type": "stat",
        "title": title,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": {"type": "prometheus", "uid": "prometheus"},
        "targets": [
            {
                "refId": "A",
                "expr": expr,
                "legendFormat": "",
                "datasource": {"type": "prometheus", "uid": "prometheus"}
            }
        ],
        "options": {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}, "orientation": "auto"}
    }


def panel_graph(panel_id: int, title: str, targets: list[dict], x: int, y: int, w: int = 12, h: int = 8) -> dict:
    return {
        "id": panel_id,
        "type": "graph",
        "title": title,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "datasource": {"type": "prometheus", "uid": "prometheus"},
        "lines": True,
        "linewidth": 2,
        "nullPointMode": "connected",
        "targets": targets,
        "legend": {"show": True}
    }


def build_dashboard(services: list[str]) -> dict:
    panels: list[dict] = []
    y = 0
    panel_id = 1

    for svc in services:
        name = svc
        metric_prefix = name

        # Row title via text panel
        panels.append({
            "id": panel_id,
            "type": "text",
            "title": f"{name} Service",
            "gridPos": {"h": 1, "w": 24, "x": 0, "y": y},
            "options": {"content": f"<h3>{name} Service</h3>", "mode": "html"}
        })
        panel_id += 1
        y += 1

        # RPS
        expr_rps = f"sum(rate({metric_prefix}_http_requests_total[1m]))"
        panels.append(panel_stat(panel_id, "Requests/sec", expr_rps, x=0, y=y))
        panel_id += 1

        # Error %
        expr_err = (
            f"100 * sum(rate({metric_prefix}_http_requests_total{{status=~\"5..|4..\"}}[5m])) / "
            f"sum(rate({metric_prefix}_http_requests_total[5m]))"
        )
        panels.append(panel_stat(panel_id, "Error % (4xx/5xx)", expr_err, x=6, y=y))
        panel_id += 1

        # p50 duration (ms)
        expr_p50 = (
            f"1000 * histogram_quantile(0.5, sum(rate({metric_prefix}_http_request_duration_seconds_bucket[5m])) by (le))"
        )
        panels.append(panel_stat(panel_id, "p50 Latency (ms)", expr_p50, x=12, y=y))
        panel_id += 1

        # p95 duration (ms)
        expr_p95 = (
            f"1000 * histogram_quantile(0.95, sum(rate({metric_prefix}_http_request_duration_seconds_bucket[5m])) by (le))"
        )
        panels.append(panel_stat(panel_id, "p95 Latency (ms)", expr_p95, x=18, y=y))
        panel_id += 1

        y += 6

        # Requests by status
        targets_status = [{
            "refId": "A",
            "expr": f"sum by (status) (rate({metric_prefix}_http_requests_total[5m]))",
            "legendFormat": "{{status}}",
            "datasource": {"type": "prometheus", "uid": "prometheus"}
        }]
        panels.append(panel_graph(panel_id, "Requests/sec by status", targets_status, x=0, y=y, w=12, h=8))
        panel_id += 1

        # Latency trend (p95)
        targets_p95 = [{
            "refId": "A",
            "expr": expr_p95,
            "legendFormat": "p95",
            "datasource": {"type": "prometheus", "uid": "prometheus"}
        }]
        panels.append(panel_graph(panel_id, "Latency p95 (ms)", targets_p95, x=12, y=y, w=12, h=8))
        panel_id += 1

        y += 8

    dashboard = {
        "title": "BT_API Service Traffic",
        "uid": "bt-api-service-traffic",
        "timezone": "browser",
        "schemaVersion": 36,
        "version": 1,
        "refresh": "15s",
        "time": {"from": "now-6h", "to": "now"},
        "panels": panels,
        "templating": {"list": []},
        "annotations": {"list": []}
    }

    return {"dashboard": dashboard, "overwrite": True}


def main() -> int:
    services = load_services_from_compose()
    payload = build_dashboard(services)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())



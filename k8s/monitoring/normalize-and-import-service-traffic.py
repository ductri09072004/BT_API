#!/usr/bin/env python3
"""
Normalize the user-provided bt-api-service-traffic.json to match available metrics
by rewriting PromQL (django_* -> metric name regex) and set Prometheus datasource,
then import into Grafana.
"""

import json
import os
import re
from pathlib import Path
import requests


BASE_DIR = Path(__file__).parent
SOURCE = BASE_DIR / "bt-api-service-traffic.json"
PROM_UID = "prometheus"


def set_prometheus_datasource(panel: dict) -> None:
    panel["datasource"] = {"type": "prometheus", "uid": PROM_UID}
    for target in panel.get("targets", []) or []:
        if isinstance(target, dict):
            target["datasource"] = {"type": "prometheus", "uid": PROM_UID}


def rewrite_expr(expr: str) -> str:
    """Rewrite PromQL metric selectors to use name-regex and merge label sets safely.

    Rewrites:
      django_http_requests_total{...} -> {__name__=~".*_http_requests_total", <labels minus job>}
      django_http_request_duration_seconds_bucket{...} -> {__name__=~".*_http_request_duration_seconds_bucket", <labels minus job>}
      django_http_request_duration_seconds_sum{...} -> {__name__=~".*_http_request_duration_seconds_sum", <labels minus job>}
    Also removes groupings by (job).
    """
    new_expr = expr

    def merge_selector(match, name_regex: str) -> str:
        full = match.group(0)
        sel = match.group('sel') or ''
        labels = sel[1:-1] if sel.startswith('{') and sel.endswith('}') else ''
        # remove labels that often don't exist in current metrics
        labels = re.sub(r",?\s*(job|status|method)\s*!?~?=\s*\"[^\"]*\"\s*", "", labels)
        labels = re.sub(r"^\s*,\s*|\s*,\s*$", "", labels)
        # rebuild
        if labels.strip():
            return '{' + f"__name__=~\"{name_regex}\",{labels}" + '}'
        return '{' + f"__name__=~\"{name_regex}\"" + '}'

    # django_http_requests_total with optional selector
    new_expr = re.sub(r"django_http_requests_total(?P<sel>\{[^}]*\})?",
                      lambda m: merge_selector(m, ".*_http_requests_total"), new_expr)

    # duration bucket
    new_expr = re.sub(r"django_http_request_duration_seconds_bucket(?P<sel>\{[^}]*\})?",
                      lambda m: merge_selector(m, ".*_http_request_duration_seconds_bucket"), new_expr)

    # duration sum
    new_expr = re.sub(r"django_http_request_duration_seconds_sum(?P<sel>\{[^}]*\})?",
                      lambda m: merge_selector(m, ".*_http_request_duration_seconds_sum"), new_expr)

    # Drop groupings by labels that may not exist
    new_expr = re.sub(r"by\s*\(\s*job\s*\)", "", new_expr)
    new_expr = re.sub(r"by\s*\(\s*status\s*\)", "", new_expr)
    new_expr = re.sub(r"by\s*\(\s*method\s*\)", "", new_expr)

    return new_expr


def normalize_dashboard(dash: dict) -> dict:
    dash = dict(dash)
    dash.pop("__inputs", None)

    # Normalize all panels
    def walk(panels):
        for p in panels:
            if not isinstance(p, dict):
                continue
            set_prometheus_datasource(p)
            # Rewrite targets
            for t in p.get("targets", []) or []:
                if isinstance(t, dict) and isinstance(t.get("expr"), str):
                    t["expr"] = rewrite_expr(t["expr"])
                    # Clean legend referencing labels that may be removed
                    lf = t.get("legendFormat")
                    if isinstance(lf, str):
                        if "{{job}}" in lf or "{{status}}" in lf or "{{method}}" in lf:
                            t["legendFormat"] = ""
            # Nested panels
            if isinstance(p.get("panels"), list):
                walk(p["panels"])

    if isinstance(dash.get("panels"), list):
        walk(dash["panels"])

    return dash


def import_to_grafana(dashboard: dict) -> bool:
    payload = {"dashboard": dashboard, "overwrite": True}
    base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
    url = f"{base_url}/api/dashboards/db"
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Import failed ({resp.status_code}): {resp.text}")
        return False
    print("Dashboard imported successfully!")
    print("Grafana:", base_url)
    return True


def main() -> int:
    global PROM_UID
    # Detect Prometheus datasource UID to avoid mismatch
    try:
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        ds_url = f"{base_url}/api/datasources"
        headers = {"Content-Type": "application/json"}
        resp = requests.get(ds_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            for ds in resp.json():
                if ds.get("type") == "prometheus":
                    PROM_UID = ds.get("uid") or PROM_UID
                    break
    except Exception:
        pass

    try:
        with SOURCE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"Failed to read {SOURCE}: {e}")
        return 1

    dashboard = normalize_dashboard(raw)
    # Persist normalized dashboard back to source file for future edits/imports
    try:
        with SOURCE.open("w", encoding="utf-8") as f:
            json.dump(dashboard, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    ok = import_to_grafana(dashboard)
    return 0 if ok else 2


if __name__ == "__main__":
    import sys
    sys.exit(main())



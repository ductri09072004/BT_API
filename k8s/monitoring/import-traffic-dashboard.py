#!/usr/bin/env python3
"""
Import the BT_API Traffic & Performance dashboard into Grafana.
"""
import json
import os
from pathlib import Path
import requests


def import_dashboard(file_path: Path) -> bool:
    try:
        with file_path.open('r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

    # Ensure wrapper fields
    if 'dashboard' not in payload:
        payload = {"dashboard": payload}
    payload.setdefault('overwrite', True)

    base_url = os.getenv('GF_URL', 'http://admin:admin123@localhost:3000')
    url = f"{base_url}/api/dashboards/db"
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Import failed ({resp.status_code}): {resp.text}")
        return False

    print("✅ BT_API Traffic & Performance dashboard imported!")
    print("🌐 http://localhost:3000")
    return True


if __name__ == '__main__':
    dashboard_path = Path(__file__).parent / 'bt-api-traffic-dashboard.json'
    import_dashboard(dashboard_path)



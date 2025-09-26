#!/usr/bin/env python3
"""
Script để import service details dashboard
"""

import requests
import json
import time
import os
from pathlib import Path

def import_service_dashboard():
    """Import BT_API service details dashboard"""
    
    # Đọc dashboard JSON
    try:
        script_dir = Path(__file__).parent
        dashboard_file = script_dir / 'service-details-dashboard.json'
        with dashboard_file.open('r', encoding='utf-8') as f:
            dashboard_wrapper = json.load(f)
    except Exception as e:
        print(f"❌ Error reading dashboard file: {e}")
        return False
    
    # Import dashboard
    try:
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        url = f"{base_url}/api/dashboards/db"
        headers = {"Content-Type": "application/json"}

        # Đảm bảo có uid cố định và overwrite
        try:
            dashboard = dashboard_wrapper.get('dashboard', {})
            if 'uid' not in dashboard or not dashboard['uid']:
                dashboard['uid'] = 'bt-api-service-details'
            dashboard_wrapper['dashboard'] = dashboard
            dashboard_wrapper['overwrite'] = True
        except Exception:
            pass

        response = requests.post(url, json=dashboard_wrapper, headers=headers)
        if response.status_code != 200:
            # Fallback to Grafana on NodePort if running via kube stack
            fallback = "http://admin:admin123@localhost:30000"
            if base_url != fallback:
                print(f"ℹ️ Primary Grafana import failed ({response.status_code}). Retrying on {fallback}...")
                url = f"{fallback}/api/dashboards/db"
                response = requests.post(url, json=dashboard_wrapper, headers=headers)
        
        if response.status_code == 200:
            print("✅ Service Details Dashboard imported successfully!")
            print("🌐 Access: http://localhost:3000")
            print("📊 Dashboard: BT_API Service Details")
            return True
        else:
            print(f"❌ Failed to import dashboard: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing dashboard: {e}")
        return False

if __name__ == "__main__":
    import_service_dashboard()

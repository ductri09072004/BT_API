#!/usr/bin/env python3
"""
Script để tự động import dashboard vào Grafana
"""

import requests
import json
import time

def import_dashboard():
    """Import BT_API dashboard vào Grafana"""
    
    # Đợi Grafana khởi động
    print("⏳ Waiting for Grafana to start...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Grafana is ready!")
                break
        except:
            time.sleep(2)
    else:
        print("❌ Grafana failed to start")
        return False
    
    # Đọc dashboard JSON
    try:
        with open('bt-api-dashboard.json', 'r') as f:
            dashboard = json.load(f)
    except Exception as e:
        print(f"❌ Error reading dashboard file: {e}")
        return False
    
    # Import dashboard
    try:
        url = "http://admin:admin123@localhost:3000/api/dashboards/db"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=dashboard, headers=headers)
        
        if response.status_code == 200:
            print("✅ Dashboard imported successfully!")
            print("🌐 Access: http://localhost:3000")
            return True
        else:
            print(f"❌ Failed to import dashboard: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing dashboard: {e}")
        return False

if __name__ == "__main__":
    import_dashboard()

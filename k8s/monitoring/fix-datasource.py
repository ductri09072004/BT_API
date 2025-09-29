#!/usr/bin/env python3
"""
Script để tạo Prometheus data source trong Grafana
Usage: python fix-datasource.py
"""

import json
import requests
import os

def create_prometheus_datasource():
    """Tạo Prometheus data source trong Grafana"""
    print("[INFO] Đang tạo Prometheus data source...")
    
    # Cấu hình data source
    datasource_config = {
        "name": "Prometheus",
        "type": "prometheus",
        "uid": "prometheus",
        "url": "http://prometheus:9090",
        "access": "proxy",
        "isDefault": True,
        "jsonData": {
            "httpMethod": "POST",
            "queryTimeout": "60s",
            "timeInterval": "5s"
        }
    }
    
    try:
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        url = f"{base_url}/api/datasources"
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=datasource_config, headers=headers)
        
        if response.status_code == 200:
            print("[SUCCESS] Prometheus data source đã được tạo thành công!")
            return True
        elif response.status_code == 409:
            print("[INFO] Prometheus data source đã tồn tại")
            return True
        else:
            print(f"[ERROR] Không thể tạo data source: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Lỗi tạo data source: {e}")
        return False

def check_existing_datasources():
    """Kiểm tra data source hiện có"""
    print("[INFO] Đang kiểm tra data source hiện có...")
    
    try:
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        url = f"{base_url}/api/datasources"
        
        response = requests.get(url)
        if response.status_code == 200:
            datasources = response.json()
            print(f"[INFO] Tìm thấy {len(datasources)} data source:")
            for ds in datasources:
                print(f"  - {ds.get('name')} (type: {ds.get('type')}, uid: {ds.get('uid')})")
            return datasources
        else:
            print(f"[ERROR] Không thể lấy danh sách data source: {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] Lỗi kiểm tra data source: {e}")
        return []

def update_dashboard_datasource():
    """Cập nhật dashboard để sử dụng data source đúng"""
    print("[INFO] Đang cập nhật dashboard...")
    
    try:
        # Đọc dashboard
        with open("service-details-dashboard.json", 'r', encoding='utf-8') as f:
            dashboard = json.load(f)
        
        # Cập nhật data source cho tất cả panels
        panels = dashboard.get("dashboard", {}).get("panels", [])
        updated_panels = 0
        
        for panel in panels:
            # Cập nhật data source cho panel
            if "datasource" not in panel:
                panel["datasource"] = {
                    "type": "prometheus",
                    "uid": "prometheus"
                }
                updated_panels += 1
            
            # Cập nhật data source cho targets
            targets = panel.get("targets", [])
            for target in targets:
                if "datasource" not in target:
                    target["datasource"] = {
                        "type": "prometheus",
                        "uid": "prometheus"
                    }
                    updated_panels += 1
        
        # Lưu dashboard
        with open("service-details-dashboard.json", 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Đã cập nhật {updated_panels} data source references")
        return True
        
    except Exception as e:
        print(f"[ERROR] Lỗi cập nhật dashboard: {e}")
        return False

def import_dashboard():
    """Import dashboard vào Grafana"""
    print("[INFO] Đang import dashboard vào Grafana...")
    
    try:
        # Đọc dashboard
        with open("service-details-dashboard.json", 'r', encoding='utf-8') as f:
            dashboard_wrapper = json.load(f)
        
        # Import dashboard
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        url = f"{base_url}/api/dashboards/db"
        headers = {"Content-Type": "application/json"}
        
        # Đảm bảo có uid và overwrite
        dashboard = dashboard_wrapper.get('dashboard', {})
        if 'uid' not in dashboard or not dashboard['uid']:
            dashboard['uid'] = 'bt-api-service-details'
        dashboard_wrapper['dashboard'] = dashboard
        dashboard_wrapper['overwrite'] = True
        
        response = requests.post(url, json=dashboard_wrapper, headers=headers)
        
        if response.status_code == 200:
            print("[SUCCESS] Dashboard đã được import thành công!")
            return True
        else:
            print(f"[WARNING] Không thể import dashboard: {response.status_code}")
            print(f"[WARNING] Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Lỗi import dashboard: {e}")
        return False

def main():
    """Main function"""
    print("=== Grafana Data Source Fixer ===")
    print("Script sẽ tạo Prometheus data source và sửa dashboard")
    print()
    
    # Kiểm tra data source hiện có
    existing_ds = check_existing_datasources()
    print()
    
    # Tạo Prometheus data source
    ds_created = create_prometheus_datasource()
    print()
    
    # Cập nhật dashboard
    dashboard_updated = update_dashboard_datasource()
    print()
    
    # Import dashboard
    if ds_created and dashboard_updated:
        import_success = import_dashboard()
        print()
        
        if import_success:
            print("[SUCCESS] Hoàn tất! Dashboard đã được sửa và import")
            print("[INFO] Truy cập: http://localhost:3000")
            print("[INFO] Username: admin, Password: admin123")
        else:
            print("[WARNING] Data source đã được tạo nhưng dashboard chưa import")
            print("[INFO] Bạn có thể import thủ công file service-details-dashboard.json")
    else:
        print("[ERROR] Không thể hoàn tất quá trình sửa lỗi")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

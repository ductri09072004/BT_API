#!/usr/bin/env python3
"""
Script để sửa lỗi Live Measurements trong Grafana
Usage: python fix-live-data.py
"""

import json
import os
import requests
from pathlib import Path

def check_prometheus_connection():
    """Kiểm tra kết nối Prometheus"""
    print("[INFO] Đang kiểm tra kết nối Prometheus...")
    
    try:
        # Kiểm tra Prometheus endpoint
        prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        response = requests.get(f"{prometheus_url}/api/v1/query?query=up", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("[SUCCESS] Prometheus đang hoạt động")
                return True
            else:
                print(f"[ERROR] Prometheus trả về lỗi: {data}")
                return False
        else:
            print(f"[ERROR] Không thể kết nối Prometheus: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Lỗi kết nối Prometheus: {e}")
        return False

def check_grafana_datasource():
    """Kiểm tra data source trong Grafana"""
    print("[INFO] Đang kiểm tra data source trong Grafana...")
    
    try:
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        url = f"{base_url}/api/datasources"
        
        response = requests.get(url)
        if response.status_code == 200:
            datasources = response.json()
            prometheus_ds = None
            
            for ds in datasources:
                if ds.get("type") == "prometheus":
                    prometheus_ds = ds
                    break
            
            if prometheus_ds:
                print(f"[SUCCESS] Tìm thấy Prometheus data source: {prometheus_ds.get('name')}")
                print(f"[INFO] URL: {prometheus_ds.get('url')}")
                print(f"[INFO] UID: {prometheus_ds.get('uid')}")
                
                # Test data source
                test_url = f"{base_url}/api/datasources/{prometheus_ds['id']}/health"
                test_response = requests.get(test_url)
                if test_response.status_code == 200:
                    print("[SUCCESS] Data source hoạt động bình thường")
                    return True
                else:
                    print(f"[WARNING] Data source có vấn đề: {test_response.status_code}")
                    return False
            else:
                print("[ERROR] Không tìm thấy Prometheus data source")
                return False
        else:
            print(f"[ERROR] Không thể kiểm tra data source: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Lỗi kiểm tra data source: {e}")
        return False

def check_dashboard_config():
    """Kiểm tra cấu hình dashboard"""
    print("[INFO] Đang kiểm tra cấu hình dashboard...")
    
    dashboard_file = Path("service-details-dashboard.json")
    if not dashboard_file.exists():
        print("[ERROR] Không tìm thấy service-details-dashboard.json")
        return False
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard = json.load(f)
        
        dashboard_config = dashboard.get("dashboard", {})
        
        # Kiểm tra refresh interval
        refresh = dashboard_config.get("refresh")
        if refresh:
            print(f"[INFO] Refresh interval: {refresh}")
        else:
            print("[WARNING] Không có refresh interval")
        
        # Kiểm tra live mode
        live_now = dashboard_config.get("liveNow")
        if live_now:
            print("[SUCCESS] Live mode đã được bật")
        else:
            print("[WARNING] Live mode chưa được bật")
        
        # Kiểm tra panels
        panels = dashboard_config.get("panels", [])
        print(f"[INFO] Số lượng panels: {len(panels)}")
        
        # Kiểm tra data source trong panels
        panels_with_datasource = 0
        for panel in panels:
            if "datasource" in panel:
                panels_with_datasource += 1
        
        print(f"[INFO] Panels có data source: {panels_with_datasource}/{len(panels)}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Lỗi đọc dashboard: {e}")
        return False

def test_prometheus_queries():
    """Test các Prometheus queries"""
    print("[INFO] Đang test Prometheus queries...")
    
    queries = [
        "up",
        "kube_pod_status_phase{namespace=\"bt-api\"}",
        "container_cpu_usage_seconds_total{namespace=\"bt-api\"}",
        "container_memory_working_set_bytes{namespace=\"bt-api\"}"
    ]
    
    prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
    
    for query in queries:
        try:
            response = requests.get(f"{prometheus_url}/api/v1/query?query={query}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    result = data.get("data", {}).get("result", [])
                    print(f"[SUCCESS] Query '{query}': {len(result)} kết quả")
                else:
                    print(f"[WARNING] Query '{query}' trả về lỗi: {data}")
            else:
                print(f"[WARNING] Query '{query}' thất bại: {response.status_code}")
        except Exception as e:
            print(f"[WARNING] Lỗi test query '{query}': {e}")

def main():
    """Main function"""
    print("=== Grafana Live Data Troubleshooter ===")
    print("Script sẽ kiểm tra và sửa lỗi Live Measurements")
    print()
    
    # Kiểm tra Prometheus
    prometheus_ok = check_prometheus_connection()
    print()
    
    # Test Prometheus queries
    test_prometheus_queries()
    print()
    
    # Kiểm tra Grafana data source
    datasource_ok = check_grafana_datasource()
    print()
    
    # Kiểm tra dashboard config
    dashboard_ok = check_dashboard_config()
    print()
    
    # Tổng kết
    print("=== TỔNG KẾT ===")
    if prometheus_ok and datasource_ok and dashboard_ok:
        print("[SUCCESS] Tất cả kiểm tra đều OK!")
        print("[INFO] Live Measurements sẽ hoạt động bình thường")
    else:
        print("[WARNING] Có một số vấn đề cần sửa:")
        if not prometheus_ok:
            print("  - Prometheus không hoạt động hoặc không thể kết nối")
        if not datasource_ok:
            print("  - Grafana data source không đúng")
        if not dashboard_ok:
            print("  - Dashboard config có vấn đề")
        
        print()
        print("[INFO] Để sửa lỗi:")
        print("1. Kiểm tra Prometheus đang chạy: docker ps | grep prometheus")
        print("2. Kiểm tra Grafana data source: http://localhost:3000/datasources")
        print("3. Chạy lại script update-dashboard.py")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

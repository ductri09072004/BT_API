#!/usr/bin/env python3
"""
Script để tự động cập nhật Grafana dashboard dựa trên services hiện có
Usage: python update-dashboard.py
"""

import json
import yaml
import os
import re
import requests
import time
from pathlib import Path

def load_docker_compose():
    """Đọc danh sách services và ports từ docker-compose.yml"""
    docker_compose_file = Path("../../docker-compose.yml")
    if not docker_compose_file.exists():
        print("[ERROR] Không tìm thấy docker-compose.yml")
        return {}
    
    try:
        with open(docker_compose_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML
        compose_data = yaml.safe_load(content)
        services_data = compose_data.get('services', {})
        
        # Lấy thông tin services và ports
        service_ports = {}
        for service_name, service_config in services_data.items():
            # Bỏ qua các service monitoring
            if 'monitoring' in service_name.lower() or 'grafana' in service_name.lower() or 'prometheus' in service_name.lower():
                continue
            
            # Tìm port từ ports mapping
            ports = service_config.get('ports', [])
            for port_mapping in ports:
                if isinstance(port_mapping, str):
                    # Format: "8000:8000"
                    if ':' in port_mapping:
                        host_port, container_port = port_mapping.split(':')
                        if container_port == '8000':  # Container port luôn là 8000
                            service_ports[service_name] = int(host_port)
                            break
                elif isinstance(port_mapping, dict):
                    # Format: {target: 8000, published: 8000}
                    if port_mapping.get('target') == 8000:
                        service_ports[service_name] = int(port_mapping.get('published', 8000))
                        break
        
        print(f"[INFO] Tìm thấy {len(service_ports)} services với ports:")
        for service, port in service_ports.items():
            print(f"  - {service}: {port}")
        
        return service_ports
    except Exception as e:
        print(f"[ERROR] Lỗi đọc docker-compose.yml: {e}")
        return {}

def load_dashboard():
    """Đọc dashboard hiện tại"""
    dashboard_file = Path("service-details-dashboard.json")
    if not dashboard_file.exists():
        print("[ERROR] Không tìm thấy service-details-dashboard.json")
        return None
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Lỗi đọc dashboard: {e}")
        return None

def save_dashboard(dashboard):
    """Lưu dashboard"""
    dashboard_file = Path("service-details-dashboard.json")
    try:
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        print(f"[SUCCESS] Đã lưu dashboard: {dashboard_file}")
        return True
    except Exception as e:
        print(f"[ERROR] Lỗi lưu dashboard: {e}")
        return False

def create_service_panel(service_name, port, panel_id):
    """Tạo panel cho service mới"""
    service_title = service_name.replace('_', ' ').replace('-', ' ').title()
    
    panel = {
        "id": panel_id,
        "title": f"{service_title} Service - CPU & Memory",
        "type": "table",
        "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
        },
        "options": {
            "showHeader": True
        },
        "targets": [
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"sum(rate(container_cpu_usage_seconds_total{{namespace=\"bt-api\", pod=~\"{service_name}.*\"}}[5m])) * 1000",
                "instant": True,
                "legendFormat": "cpu_m",
                "refId": "A",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"sum(container_memory_working_set_bytes{{namespace=\"bt-api\", pod=~\"{service_name}.*\"}}) / 1024 / 1024",
                "instant": True,
                "legendFormat": "mem_mi",
                "refId": "B",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"sum(kube_pod_container_resource_requests{{namespace=\"bt-api\", pod=~\"{service_name}.*\", resource=\"cpu\"}}) * 1000",
                "instant": True,
                "legendFormat": "cpu_request_m",
                "refId": "C",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"sum(kube_pod_container_resource_limits{{namespace=\"bt-api\", pod=~\"{service_name}.*\", resource=\"cpu\"}}) * 1000",
                "instant": True,
                "legendFormat": "cpu_limit_m",
                "refId": "D",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"sum(kube_pod_container_resource_requests{{namespace=\"bt-api\", pod=~\"{service_name}.*\", resource=\"memory\"}}) / 1024 / 1024",
                "instant": True,
                "legendFormat": "mem_request_mi",
                "refId": "E",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"sum(kube_pod_container_resource_limits{{namespace=\"bt-api\", pod=~\"{service_name}.*\", resource=\"memory\"}}) / 1024 / 1024",
                "instant": True,
                "legendFormat": "mem_limit_mi",
                "refId": "F",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"(sum(rate(container_cpu_usage_seconds_total{{namespace=\"bt-api\", pod=~\"{service_name}.*\"}}[5m])) / sum(kube_pod_container_resource_limits{{namespace=\"bt-api\", pod=~\"{service_name}.*\", resource=\"cpu\"}})) * 100",
                "instant": True,
                "legendFormat": "cpu_util_percent",
                "refId": "G",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"(sum(container_memory_working_set_bytes{{namespace=\"bt-api\", pod=~\"{service_name}.*\"}}) / sum(kube_pod_container_resource_limits{{namespace=\"bt-api\", pod=~\"{service_name}.*\", resource=\"memory\"}})) * 100",
                "instant": True,
                "legendFormat": "mem_util_percent",
                "refId": "H",
                "queryType": "timeSeriesQuery"
            }
        ],
        "transformations": [
            {
                "id": "reduce",
                "options": {
                    "reducers": [
                        "last"
                    ],
                    "labelsToFields": True
                }
            },
            {
                "id": "rowsToFields",
                "options": {
                    "fieldName": "Field",
                    "valueName": "Last"
                }
            },
            {
                "id": "organize",
                "options": {
                    "excludeByName": {
                        "Time": True
                    },
                    "renameByName": {
                        "A-series": "cpu_m",
                        "B-series": "mem_mi",
                        "C-series": "cpu_request_m",
                        "D-series": "cpu_limit_m",
                        "E-series": "mem_request_mi",
                        "F-series": "mem_limit_mi",
                        "G-series": "cpu_util_percent",
                        "H-series": "mem_util_percent"
                    }
                }
            }
        ],
        "gridPos": {
            "h": 4,
            "w": 24,
            "x": 0,
            "y": 0  # Sẽ được cập nhật sau
        }
    }
    
    return panel

def get_existing_service_panels(dashboard):
    """Lấy danh sách panels của services hiện có"""
    existing_services = {}
    panels = dashboard.get("dashboard", {}).get("panels", [])
    
    for panel in panels:
        title = panel.get("title", "")
        # Tìm panel có format "Service Name Service - CPU & Memory"
        match = re.search(r"^(.+?) Service - CPU & Memory$", title)
        if match:
            service_name = match.group(1).lower().replace(' ', '_').replace('-', '_')
            existing_services[service_name] = {
                "panel": panel,
                "title": title,
                "id": panel.get("id")
            }
    
    return existing_services

def ensure_prometheus_datasource(dashboard):
    """Đảm bảo tất cả panels sử dụng Prometheus data source"""
    panels = dashboard.get("dashboard", {}).get("panels", [])
    
    for panel in panels:
        # Thêm data source cho panel nếu chưa có
        if "datasource" not in panel:
            panel["datasource"] = {
                "type": "prometheus",
                "uid": "prometheus"
            }
        
        # Cập nhật data source cho tất cả targets
        targets = panel.get("targets", [])
        for target in targets:
            if "datasource" not in target:
                target["datasource"] = {
                    "type": "prometheus",
                    "uid": "prometheus"
                }
            # Đảm bảo target có format đúng cho Prometheus
            if "expr" in target and "refId" not in target:
                target["refId"] = "A"
            if "expr" in target and "queryType" not in target:
                target["queryType"] = "timeSeriesQuery"
    
    return dashboard

def update_prometheus_config(service_ports):
    """Cập nhật Prometheus config với services mới"""
    print("[INFO] Đang cập nhật Prometheus config...")
    
    # Tạo targets list từ services và ports thực tế
    targets = []
    for service_name, port in service_ports.items():
        targets.append(f"'host.docker.internal:{port}'  # {service_name} service")
    
    # Tạo Prometheus config mới
    prometheus_config = f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  # Kubernetes API server
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
    - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
      action: keep
      regex: default;kubernetes;https

  # Kubernetes nodes
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
    - role: node
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
    - action: labelmap
      regex: __meta_kubernetes_node_label_(.+)

  # Kubernetes pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\\d+)
      replacement: $1:$2
      target_label: __address__
    - action: labelmap
      regex: __meta_kubernetes_pod_label_(.+)
    - source_labels: [__meta_kubernetes_namespace]
      action: replace
      target_label: kubernetes_namespace
    - source_labels: [__meta_kubernetes_pod_name]
      action: replace
      target_label: kubernetes_pod_name

  # BT_API services
  - job_name: 'bt-api-services'
    static_configs:
    - targets: 
{chr(10).join(f"      - {target}" for target in targets)}
    metrics_path: /metrics
    scrape_interval: 30s
"""
    
    # Lưu Prometheus config
    try:
        with open("prometheus.yml", 'w', encoding='utf-8') as f:
            f.write(prometheus_config)
        print("[SUCCESS] Prometheus config đã được cập nhật")
        return True
    except Exception as e:
        print(f"[ERROR] Lỗi cập nhật Prometheus config: {e}")
        return False

def restart_prometheus():
    """Restart Prometheus để áp dụng config mới"""
    print("[INFO] Đang restart Prometheus...")
    try:
        import subprocess
        result = subprocess.run(["docker", "restart", "bt-api-prometheus"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("[SUCCESS] Prometheus đã được restart")
            return True
        else:
            print(f"[ERROR] Lỗi restart Prometheus: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Lỗi restart Prometheus: {e}")
        return False

def update_dashboard():
    """Cập nhật dashboard"""
    print("[INFO] Đang cập nhật Grafana dashboard...")
    
    # Đọc danh sách services và ports từ docker-compose.yml
    service_ports = load_docker_compose()
    if not service_ports:
        print("[ERROR] Không có services nào được tìm thấy")
        return False
    
    current_services = list(service_ports.keys())
    print(f"[INFO] Tìm thấy {len(current_services)} services: {', '.join(current_services)}")
    
    # Cập nhật Prometheus config
    if not update_prometheus_config(service_ports):
        print("[WARNING] Không thể cập nhật Prometheus config")
    
    # Restart Prometheus
    if not restart_prometheus():
        print("[WARNING] Không thể restart Prometheus")
    
    # Đọc dashboard hiện tại
    dashboard = load_dashboard()
    if not dashboard:
        return False
    
    # Đảm bảo tất cả panels sử dụng Prometheus data source
    dashboard = ensure_prometheus_datasource(dashboard)
    
    # Lấy panels hiện có
    existing_panels = get_existing_service_panels(dashboard)
    print(f"[INFO] Tìm thấy {len(existing_panels)} service panels hiện có")
    
    # Chuẩn hóa tên service để so sánh
    current_services_normalized = []
    for service in current_services:
        normalized = service.lower().replace('-', '_')
        current_services_normalized.append(normalized)
    
    # Tìm services cần thêm và xóa
    existing_services_normalized = list(existing_panels.keys())
    
    services_to_add = []
    services_to_remove = []
    
    for service in current_services_normalized:
        if service not in existing_services_normalized:
            services_to_add.append(service)
    
    for service in existing_services_normalized:
        if service not in current_services_normalized:
            services_to_remove.append(service)
    
    print(f"[INFO] Services cần thêm: {services_to_add}")
    print(f"[INFO] Services cần xóa: {services_to_remove}")
    
    # Xóa panels của services đã bị xóa
    panels = dashboard["dashboard"]["panels"]
    panels_to_remove = []
    
    for service in services_to_remove:
        if service in existing_panels:
            panel_id = existing_panels[service]["id"]
            print(f"[INFO] Xóa panel cho service: {service} (ID: {panel_id})")
            panels_to_remove.append(panel_id)
    
    # Xóa panels
    dashboard["dashboard"]["panels"] = [
        panel for panel in panels 
        if panel.get("id") not in panels_to_remove
    ]
    
    # Thêm panels cho services mới
    next_panel_id = 500  # Bắt đầu từ ID cao để tránh conflict
    max_y = 0
    
    # Tìm y position cao nhất hiện có
    for panel in dashboard["dashboard"]["panels"]:
        grid_pos = panel.get("gridPos", {})
        y_pos = grid_pos.get("y", 0)
        height = grid_pos.get("h", 1)
        max_y = max(max_y, y_pos + height)
    
    for service in services_to_add:
        # Tìm service name gốc từ docker-compose
        original_service = None
        service_port = None
        for orig in current_services:
            if orig.lower().replace('-', '_') == service:
                original_service = orig
                service_port = service_ports[orig]
                break
        
        if original_service and service_port:
            print(f"[INFO] Thêm panel cho service: {original_service} (port: {service_port})")
            new_panel = create_service_panel(original_service, service_port, next_panel_id)
            new_panel["gridPos"]["y"] = max_y
            dashboard["dashboard"]["panels"].append(new_panel)
            max_y += 4  # Mỗi panel cao 4
            next_panel_id += 1
    
    # Đảm bảo dashboard có cấu hình refresh và time range phù hợp cho Live Measurements
    dashboard_config = dashboard.get("dashboard", {})
    dashboard_config["refresh"] = "5s"  # Refresh mỗi 5 giây cho live data
    dashboard_config["time"] = {
        "from": "now-5m",
        "to": "now"
    }
    dashboard_config["liveNow"] = True  # Bật live mode
    dashboard_config["timepicker"] = {
        "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"],
        "time_options": ["5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"]
    }
    dashboard_config["templating"] = {
        "list": []
    }
    dashboard_config["annotations"] = {
        "list": []
    }
    dashboard_config["editable"] = True
    dashboard_config["gnetId"] = None
    dashboard_config["graphTooltip"] = 0
    dashboard_config["links"] = []
    dashboard_config["schemaVersion"] = 27
    dashboard_config["style"] = "dark"
    dashboard_config["version"] = 1
    
    # Lưu dashboard
    if save_dashboard(dashboard):
        print("[SUCCESS] Dashboard đã được cập nhật thành công!")
        print(f"[INFO] Tổng cộng {len(services_to_add)} panels được thêm, {len(services_to_remove)} panels được xóa")
        print("[INFO] Dashboard đã được cấu hình cho Live Measurements (refresh: 5s)")
        return True
    
    return False

def check_prometheus_datasource():
    """Kiểm tra Prometheus data source có tồn tại không"""
    try:
        base_url = os.getenv("GF_URL", "http://admin:admin123@localhost:3000")
        url = f"{base_url}/api/datasources"
        
        response = requests.get(url)
        if response.status_code == 200:
            datasources = response.json()
            for ds in datasources:
                if ds.get("type") == "prometheus" and ds.get("uid") == "prometheus":
                    print(f"[SUCCESS] Tìm thấy Prometheus data source: {ds.get('name')}")
                    return True
            
            print("[WARNING] Không tìm thấy Prometheus data source với UID 'prometheus'")
            print("[INFO] Các data source hiện có:")
            for ds in datasources:
                print(f"  - {ds.get('name')} (type: {ds.get('type')}, uid: {ds.get('uid')})")
            return False
        else:
            print(f"[WARNING] Không thể kiểm tra data source: {response.status_code}")
            return False
    except Exception as e:
        print(f"[WARNING] Lỗi kiểm tra data source: {e}")
        return False

def import_dashboard_to_grafana():
    """Import dashboard vào Grafana"""
    print("[INFO] Đang import dashboard vào Grafana...")
    
    # Kiểm tra Prometheus data source
    if not check_prometheus_datasource():
        print("[WARNING] Prometheus data source không tồn tại hoặc không đúng UID")
        print("[INFO] Dashboard có thể không hiển thị data live")
    
    # Đọc dashboard JSON
    try:
        dashboard_file = Path("service-details-dashboard.json")
        with dashboard_file.open('r', encoding='utf-8') as f:
            dashboard_wrapper = json.load(f)
    except Exception as e:
        print(f"[ERROR] Lỗi đọc dashboard file: {e}")
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
                print(f"[INFO] Grafana chính thất bại ({response.status_code}). Thử fallback {fallback}...")
                url = f"{fallback}/api/dashboards/db"
                response = requests.post(url, json=dashboard_wrapper, headers=headers)
        
        if response.status_code == 200:
            print("[SUCCESS] Dashboard đã được import vào Grafana thành công!")
            print("[INFO] Truy cập: http://localhost:3000")
            print("[INFO] Dashboard: BT_API Service Details")
            return True
        else:
            print(f"[WARNING] Không thể import dashboard: {response.text}")
            print("[INFO] Bạn có thể import thủ công file service-details-dashboard.json vào Grafana")
            return False
            
    except Exception as e:
        print(f"[WARNING] Lỗi import dashboard: {e}")
        print("[INFO] Bạn có thể import thủ công file service-details-dashboard.json vào Grafana")
        return False

def main():
    """Main function"""
    print("=== Grafana Dashboard Auto Updater ===")
    print("Script sẽ tự động cập nhật dashboard dựa trên services trong docker-compose.yml")
    print()
    
    success = update_dashboard()
    
    if success:
        print()
        print("[SUCCESS] Cập nhật dashboard hoàn tất!")
        
        # Tự động import vào Grafana
        print()
        import_success = import_dashboard_to_grafana()
        
        if import_success:
            print()
            print("[SUCCESS] Quá trình hoàn tất! Dashboard đã được cập nhật và import vào Grafana")
        else:
            print()
            print("[INFO] Dashboard đã được cập nhật nhưng chưa import vào Grafana")
            print("[INFO] Bạn có thể import thủ công file service-details-dashboard.json vào Grafana")
    else:
        print()
        print("[ERROR] Cập nhật dashboard thất bại!")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

#!/usr/bin/env python3
"""
Script để tạo service mới từ template
Usage: python create_service.py <service_name>
"""

import os
import sys
import shutil
import re
import subprocess
import json

def create_service(service_name):
    """Tạo service mới từ template"""
    
    # Validate service name
    if not service_name or not service_name.replace('-', '').replace('_', '').isalnum():
        print("[ERROR] Service name chi duoc chua chu cai, so, dau gach ngang va gach duoi")
        return False
    
    template_dir = "services/template"
    service_dir = f"services/{service_name}"
    
    # Kiểm tra service đã tồn tại chưa
    if os.path.exists(service_dir):
        print(f"[ERROR] Service '{service_name}' da ton tai!")
        return False
    
    try:
        # Copy template
        shutil.copytree(template_dir, service_dir)
        print(f"✅ Đã copy template → {service_dir}")
        
        # Đảm bảo file db.py được copy (nếu có trong template)
        template_db = os.path.join(template_dir, "db.py")
        service_db = os.path.join(service_dir, "db.py")
        if os.path.exists(template_db) and not os.path.exists(service_db):
            shutil.copy2(template_db, service_db)
            print(f"✅ Đã copy file db.py")
        
        # Cập nhật tên service trong main.py
        main_file = os.path.join(service_dir, "main.py")
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Thay thế title="Template" bằng tên service mới
        service_title = service_name.replace('-', ' ').replace('_', ' ').title()
        content = content.replace('title="Template"', f'title="{service_title}"')
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Đã cập nhật tên service: {service_title}")
        
        # Tạo file .env.example
        env_file = os.path.join(service_dir, ".env.example")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(f"# {service_title} Environment Variables\n")
            f.write("PORT=8000\n")
            f.write("DEBUG=true\n")
            f.write("MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=AppName\n")
            f.write("MONGODB_DB=TPExpress\n")
        
        print(f"✅ Đã tạo file .env.example")
        
        print(f"\n[SUCCESS] Service '{service_name}' da duoc tao thanh cong!")
        print(f"[INFO] Thu muc: {service_dir}")
        print(f"[INFO] De chay service: cd {service_dir} && python main.py")
        print(f"[INFO] De build Docker: cd {service_dir} && docker build -t {service_name} .")
        
        # Tự động cập nhật docker-compose.yml
        print(f"\n[INFO] Dang cap nhat docker-compose.yml...")
        try:
            # Tìm port trống (bắt đầu từ 8005)
            docker_compose_file = "docker-compose.yml"
            if os.path.exists(docker_compose_file):
                with open(docker_compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tìm port cao nhất
                ports = re.findall(r'"(\d+):8000"', content)
                if ports:
                    next_port = max(int(p) for p in ports) + 1
                else:
                    next_port = 8005
                
                # Cập nhật docker-compose.yml
                result = subprocess.run([
                    sys.executable, "update_docker_compose.py", service_name, str(next_port)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"[SUCCESS] Da tu dong cap nhat docker-compose.yml voi port {next_port}")
                else:
                    print(f"[WARNING] Khong the tu dong cap nhat docker-compose.yml: {result.stderr}")
                    print(f"[INFO] Hay them service '{service_name}' vao docker-compose.yml thu cong")
            else:
                print(f"[WARNING] Khong tim thay docker-compose.yml")
        except Exception as e:
            print(f"[WARNING] Loi khi cap nhat docker-compose.yml: {e}")
            print(f"[INFO] Hay them service '{service_name}' vao docker-compose.yml thu cong")
        
        # Tự động cập nhật dashboard
        print(f"\n[INFO] Dang cap nhat dashboard...")
        try:
            update_dashboard_for_service(service_name, next_port)
            print(f"[SUCCESS] Da tu dong cap nhat dashboard cho service '{service_name}'")
        except Exception as e:
            print(f"[WARNING] Khong the tu dong cap nhat dashboard: {e}")
            print(f"[INFO] Hay them service '{service_name}' vao dashboard thu cong")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Loi khi tao service: {e}")
        return False

def update_dashboard_for_service(service_name, port):
    """Tự động cập nhật dashboard cho service mới"""
    
    service_title = service_name.replace('-', ' ').replace('_', ' ').title()
    dashboard_file = "k8s/monitoring/service-details-dashboard.json"
    
    if not os.path.exists(dashboard_file):
        print(f"[WARNING] Khong tim thay dashboard file: {dashboard_file}")
        return
    
    # Đọc dashboard hiện tại
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        dashboard = json.load(f)
    
    # Tạo panel mới cho service
    new_panel = {
        "id": 1000 + len(dashboard["dashboard"]["panels"]),  # ID duy nhất
        "title": f"{service_title} Service - CPU & Memory",
        "type": "timeseries",
        "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
        },
        "targets": [
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"rate(process_cpu_seconds_total{{job=\"bt-api-services\", instance=~\"host.docker.internal:{port}\"}}[5m]) * 100",
                "instant": False,
                "legendFormat": f"{service_title} CPU Usage %",
                "refId": "A",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"process_resident_memory_bytes{{job=\"bt-api-services\", instance=~\"host.docker.internal:{port}\"}} / 1024 / 1024",
                "instant": False,
                "legendFormat": f"{service_title} Memory Used (MB)",
                "refId": "B",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": f"process_virtual_memory_bytes{{job=\"bt-api-services\", instance=~\"host.docker.internal:{port}\"}} / 1024 / 1024",
                "instant": False,
                "legendFormat": f"{service_title} Memory Virtual (MB)",
                "refId": "C",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": "512",  # Memory limit mặc định (theo script create-k8s-manifest.py)
                "instant": False,
                "legendFormat": f"{service_title} Memory Limit (MB)",
                "refId": "D",
                "queryType": "timeSeriesQuery"
            },
            {
                "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                },
                "expr": "256",  # Memory request mặc định (theo script create-k8s-manifest.py)
                "instant": False,
                "legendFormat": f"{service_title} Memory Request (MB)",
                "refId": "E",
                "queryType": "timeSeriesQuery"
            }
        ],
        "gridPos": {
            "h": 8,
            "w": 24,
            "x": 0,
            "y": len(dashboard["dashboard"]["panels"]) * 10  # Vị trí tự động
        }
    }
    
    # Thêm panel mới vào dashboard
    dashboard["dashboard"]["panels"].append(new_panel)
    
    # Cập nhật Services Performance Overview panel để bao gồm service mới
    performance_panel = None
    for panel in dashboard["dashboard"]["panels"]:
        if panel.get("title") == "Services Performance Overview":
            performance_panel = panel
            break
    
    if performance_panel:
        # Thêm CPU metric cho service mới
        new_cpu_target = {
            "datasource": {
                "type": "prometheus",
                "uid": "prometheus"
            },
            "expr": f"rate(process_cpu_seconds_total{{job=\"bt-api-services\", instance=~\"host.docker.internal:{port}\"}}[5m]) * 100",
            "instant": False,
            "legendFormat": f"{service_title} CPU %",
            "refId": f"G{len(performance_panel['targets'])}",
            "queryType": "timeSeriesQuery"
        }
        performance_panel["targets"].append(new_cpu_target)
        
        # Thêm Memory metric cho service mới
        new_memory_target = {
            "datasource": {
                "type": "prometheus",
                "uid": "prometheus"
            },
            "expr": f"process_resident_memory_bytes{{job=\"bt-api-services\", instance=~\"host.docker.internal:{port}\"}} / 1024 / 1024",
            "instant": False,
            "legendFormat": f"{service_title} Memory (MB)",
            "refId": f"H{len(performance_panel['targets'])}",
            "queryType": "timeSeriesQuery"
        }
        performance_panel["targets"].append(new_memory_target)
    
    # Ghi lại dashboard
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    
    print(f"[SUCCESS] Da them {service_title} Service vao dashboard")

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_service.py <service_name>")
        print("Example: python create_service.py payment")
        sys.exit(1)
    
    service_name = sys.argv[1]
    success = create_service(service_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

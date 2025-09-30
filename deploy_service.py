import os
import sys
import subprocess
from pathlib import Path
import json


def run(cmd: list[str]) -> int:
    print(f"[INFO] Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=False).returncode


def build_docker_image(service: str) -> int:
    context = Path("services") / service
    if not context.exists():
        print(f"[ERROR] Service folder not found: {context}")
        return 2
    image = f"bt_api-{service}:latest"
    return run(["docker", "build", "-t", image, str(context)])


def compose_build(service: str) -> int:
    # docker compose build <service>
    return run(["docker", "compose", "build", service])


def compose_up(service: str) -> int:
    # docker compose up -d <service>
    return run(["docker", "compose", "up", "-d", service])


def ensure_manifest(service: str) -> Path:
    manifests_dir = Path("k8s/manifests")
    manifests_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifests_dir / f"{service}-deployment.yaml"
    if manifest.exists():
        return manifest

    # create a minimal manifest based on template
    content = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service}-service
  namespace: bt-api
  labels:
    app: {service}-service
    service: {service}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {service}-service
  template:
    metadata:
      labels:
        app: {service}-service
        service: {service}
    spec:
      containers:
      - name: {service}-service
        image: bt_api-{service}:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          valueFrom:
            configMapKeyRef:
              name: bt-api-config
              key: DEBUG
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {service}-service
  namespace: bt-api
  labels:
    app: {service}-service
spec:
  selector:
    app: {service}-service
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
""".lstrip()
    manifest.write_text(content, encoding="utf-8")
    print(f"[SUCCESS] Created manifest: {manifest}")
    return manifest


def apply_manifest(manifest: Path) -> int:
    return run(["kubectl", "apply", "-f", str(manifest)])


def rollout_restart(service: str) -> int:
    return run(["kubectl", "rollout", "restart", f"deployment/{service}-service", "-n", "bt-api"])


def rollout_status(service: str) -> int:
    return run(["kubectl", "rollout", "status", f"deployment/{service}-service", "-n", "bt-api", "--timeout=180s"])


def update_dashboard_for_service(service_name: str, port: int):
    """Tự động cập nhật dashboard cho service mới"""
    
    service_title = service_name.replace('-', ' ').replace('_', ' ').title()
    dashboard_file = Path("k8s/monitoring/service-details-dashboard.json")
    
    if not dashboard_file.exists():
        print(f"[WARNING] Khong tim thay dashboard file: {dashboard_file}")
        return
    
    try:
        # Đọc dashboard hiện tại
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard = json.load(f)
        
        # Kiểm tra xem service đã có trong dashboard chưa
        service_panel_title = f"{service_title} Service - CPU & Memory"
        existing_panel = None
        for panel in dashboard["dashboard"]["panels"]:
            if panel.get("title") == service_panel_title:
                existing_panel = panel
                break
        
        if existing_panel:
            print(f"[INFO] Service '{service_title}' da co trong dashboard")
            return
        
        # Tạo panel mới cho service
        new_panel = {
            "id": 1000 + len(dashboard["dashboard"]["panels"]),  # ID duy nhất
            "title": service_panel_title,
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
        
        # Ghi lại dashboard
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Da them {service_title} Service vao dashboard")
        
    except Exception as e:
        print(f"[WARNING] Khong the cap nhat dashboard: {e}")
        print(f"[INFO] Hay them service '{service_title}' vao dashboard thu cong")


def find_service_port(service: str) -> int:
    """Tìm port của service từ docker-compose hoặc manifest"""
    
    # Thử tìm từ docker-compose.yml
    docker_compose_file = Path("docker-compose.yml")
    if docker_compose_file.exists():
        try:
            with open(docker_compose_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tìm pattern: "port:8000" cho service
            import re
            pattern = rf'"{service}-service":\s*\n.*?ports:\s*\n.*?"(\d+):8000"'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"[WARNING] Khong the doc docker-compose.yml: {e}")
    
    # Thử tìm từ manifest
    manifest_file = Path(f"k8s/manifests/{service}-deployment.yaml")
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tìm pattern: targetPort: 8000 trong Service
            import re
            pattern = rf'name: {service}-service.*?ports:.*?targetPort: 8000'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                # Tìm port trước targetPort
                port_pattern = r'port: (\d+)'
                port_match = re.search(port_pattern, match.group(0))
                if port_match:
                    return int(port_match.group(1))
        except Exception as e:
            print(f"[WARNING] Khong the doc manifest: {e}")
    
    # Default port nếu không tìm thấy
    print(f"[WARNING] Khong tim thay port cho service '{service}', su dung port mac dinh 8000")
    return 8000


def upsert_service_panel_in_dashboard(service: str) -> None:
    """Add a per-service table panel to k8s/monitoring/service-details-dashboard.json if missing."""
    dashboard_path = Path("k8s/monitoring/service-details-dashboard.json")
    if not dashboard_path.exists():
        print(f"[WARN] Dashboard file not found: {dashboard_path}")
        return

    try:
        data = json.loads(dashboard_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[WARN] Failed to read dashboard json: {e}")
        return

    dashboard = data.get("dashboard") or data
    panels = dashboard.get("panels", [])

    # Skip if a panel for this service already exists (by title or regex)
    wanted_title = f"{service} Service - CPU & Memory"
    for p in panels:
        if p.get("title", "").lower() == wanted_title.lower():
            print(f"[INFO] Panel already exists for service '{service}'. Skipping add.")
            return

    # Compute next id and y position
    next_id = max([p.get("id", 0) for p in panels] + [0]) + 1
    last_bottom = 0
    for p in panels:
        pos = p.get("gridPos", {})
        y = int(pos.get("y", 0))
        h = int(pos.get("h", 0))
        last_bottom = max(last_bottom, y + h)

    svc_regex = f"{service}.*"

    new_panel = {
        "id": next_id,
        "title": wanted_title,
        "type": "table",
        "options": {"showHeader": True},
        "targets": [
            {"expr": f"sum(rate(container_cpu_usage_seconds_total{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\"}}[5m])) * 1000", "instant": True, "legendFormat": "cpu_mcores"},
            {"expr": f"sum(container_memory_working_set_bytes{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\"}}) / 1024 / 1024 / 1024", "instant": True, "legendFormat": "mem_gb"},
            {"expr": f"sum(kube_pod_container_resource_requests{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\", resource=\\\"cpu\\\"}}) * 1000", "instant": True, "legendFormat": "cpu_request_mcores"},
            {"expr": f"sum(kube_pod_container_resource_limits{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\", resource=\\\"cpu\\\"}}) * 1000", "instant": True, "legendFormat": "cpu_limit_mcores"},
            {"expr": f"sum(kube_pod_container_resource_requests{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\", resource=\\\"memory\\\"}}) / 1024 / 1024 / 1024", "instant": True, "legendFormat": "mem_request_gb"},
            {"expr": f"sum(kube_pod_container_resource_limits{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\", resource=\\\"memory\\\"}}) / 1024 / 1024 / 1024", "instant": True, "legendFormat": "mem_limit_gb"},
            {"expr": f"(sum(rate(container_cpu_usage_seconds_total{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\"}}[5m])) / sum(kube_pod_container_resource_limits{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\", resource=\\\"cpu\\\"}})) * 100", "instant": True, "legendFormat": "cpu_util_percent"},
            {"expr": f"(sum(container_memory_working_set_bytes{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\"}}) / sum(kube_pod_container_resource_limits{{namespace=\\\"bt-api\\\", pod=~\\\"{svc_regex}\\\", resource=\\\"memory\\\"}})) * 100", "instant": True, "legendFormat": "mem_util_percent"}
        ],
        "transformations": [
            {"id": "reduce", "options": {"reducers": ["last"], "labelsToFields": True}},
            {"id": "rowsToFields", "options": {"fieldName": "Field", "valueName": "Last"}},
            {"id": "organize", "options": {"excludeByName": {"Time": True}, "renameByName": {"A-series": "cpu_mcores", "B-series": "mem_gb", "C-series": "cpu_request_mcores", "D-series": "cpu_limit_mcores", "E-series": "mem_request_gb", "F-series": "mem_limit_gb", "G-series": "cpu_util_percent", "H-series": "mem_util_percent"}}}
        ],
        "gridPos": {"h": 4, "w": 24, "x": 0, "y": int(last_bottom)}
    }

    panels.append(new_panel)
    dashboard["panels"] = panels
    # Preserve wrapper if exists
    if "dashboard" in data:
        data["dashboard"] = dashboard
    else:
        data = dashboard

    try:
        dashboard_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[SUCCESS] Added panel for service '{service}' to {dashboard_path}")
    except Exception as e:
        print(f"[WARN] Failed to write dashboard json: {e}")

    # Try to auto-import to Grafana if script exists
    importer = Path("k8s/monitoring/import-service-details.py")
    if importer.exists():
        print("[INFO] Importing updated Service Details dashboard to Grafana...")
        run([sys.executable, str(importer)])

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python deploy_service.py <service_name>")
        return 2

    service = sys.argv[1].strip()
    if not service:
        print("[ERROR] service_name is empty")
        return 2

    # 1) Build & run with docker compose (preferred for dev)
    code = compose_build(service)
    if code != 0:
        print("[WARN] docker compose build failed, falling back to 'docker build'.")
        if build_docker_image(service) != 0:
            return 1
    # If compose build succeeded, also bring the service up
    if code == 0:
        compose_up(service)

    manifest = ensure_manifest(service)

    if apply_manifest(manifest) != 0:
        return 1

    # Ensure pods pick the latest local image tag and wait until ready
    rollout_restart(service)
    rollout_status(service)
    # Update monitoring dashboard
    try:
        # Tìm port từ docker-compose hoặc manifest
        port = find_service_port(service)
        update_dashboard_for_service(service, port)
    except Exception as e:
        print(f"[WARNING] Khong the cap nhat dashboard: {e}")
        upsert_service_panel_in_dashboard(service)  # Fallback to old method
    print("[DONE] docker compose build/up + K8s apply/rollout complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



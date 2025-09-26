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
    upsert_service_panel_in_dashboard(service)
    print("[DONE] docker compose build/up + K8s apply/rollout complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



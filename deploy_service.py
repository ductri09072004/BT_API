import os
import sys
import subprocess
from pathlib import Path


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


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python deploy_service.py <service_name>")
        return 2

    service = sys.argv[1].strip()
    if not service:
        print("[ERROR] service_name is empty")
        return 2

    if build_docker_image(service) != 0:
        return 1

    manifest = ensure_manifest(service)

    if apply_manifest(manifest) != 0:
        return 1

    # Ensure pods pick latest local image tag
    rollout_restart(service)
    print("[DONE] Build + K8s apply complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



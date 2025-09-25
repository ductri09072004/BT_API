#!/usr/bin/env python3
"""
Script để tạo Kubernetes manifest cho service mới
Usage: python create-k8s-manifest.py <service_name>
"""

import os
import sys
import re

def create_k8s_manifest(service_name):
    """Tạo Kubernetes manifest cho service mới"""
    
    # Validate service name
    if not service_name or not service_name.replace('-', '').replace('_', '').isalnum():
        print("[ERROR] Service name chi duoc chua chu cai, so, dau gach ngang va gach duoi")
        return False
    
    service_title = service_name.replace('-', ' ').replace('_', ' ').title()
    service_camel = service_name.replace('-', '').replace('_', '')
    
    # Tạo deployment manifest
    deployment_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}-service
  namespace: bt-api
  labels:
    app: {service_name}-service
    service: {service_name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {service_name}-service
  template:
    metadata:
      labels:
        app: {service_name}-service
        service: {service_name}
    spec:
      containers:
      - name: {service_name}-service
        image: bt_api-{service_name}:latest
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
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
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
  name: {service_name}-service
  namespace: bt-api
  labels:
    app: {service_name}-service
spec:
  selector:
    app: {service_name}-service
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
"""
    
    # Ghi deployment manifest
    deployment_file = f"../manifests/{service_name}-deployment.yaml"
    try:
        with open(deployment_file, 'w', encoding='utf-8') as f:
            f.write(deployment_content)
        print(f"[SUCCESS] Da tao deployment manifest: {deployment_file}")
    except Exception as e:
        print(f"[ERROR] Loi khi tao deployment manifest: {e}")
        return False
    
    # Cập nhật ingress
    ingress_file = "../manifests/ingress.yaml"
    if os.path.exists(ingress_file):
        try:
            with open(ingress_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Thêm service vào ingress
            new_ingress_rule = f"""  - host: {service_name}.bt-api.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {service_name}-service
            port:
              number: 8000
"""
            
            # Tìm vị trí để thêm rule mới (trước comment cuối)
            if "  # payment:" in content:
                content = content.replace("  # payment:", f"{new_ingress_rule}  # payment:")
            else:
                # Thêm vào cuối file trước dòng cuối
                lines = content.split('\n')
                lines.insert(-1, new_ingress_rule)
                content = '\n'.join(lines)
            
            # Cập nhật path-based routing
            path_rule = f"""      - path: /{service_name}
        pathType: Prefix
        backend:
          service:
            name: {service_name}-service
            port:
              number: 8000
"""
            
            # Thêm vào path-based routing
            if "      - path: /payment" in content:
                content = content.replace("      - path: /payment", f"{path_rule}      - path: /payment")
            
            with open(ingress_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[SUCCESS] Da cap nhat ingress manifest")
        except Exception as e:
            print(f"[WARNING] Khong the cap nhat ingress: {e}")
    
    print(f"\n[SUCCESS] Kubernetes manifest cho service '{service_name}' da duoc tao!")
    print(f"[INFO] Deployment file: {deployment_file}")
    print(f"[INFO] De deploy service: kubectl apply -f {deployment_file}")
    print(f"[INFO] URL: http://{service_name}.bt-api.local/healthz")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python create-k8s-manifest.py <service_name>")
        print("Example: python create-k8s-manifest.py notification")
        sys.exit(1)
    
    service_name = sys.argv[1]
    success = create_k8s_manifest(service_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

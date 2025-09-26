#!/bin/bash
# Script cài đặt Prometheus + Grafana cho monitoring

echo "🚀 Installing Prometheus + Grafana Stack..."

# Thêm Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Tạo namespace cho monitoring
kubectl create namespace monitoring

# Cài đặt Prometheus + Grafana stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin123 \
  --set grafana.service.type=NodePort \
  --set grafana.service.nodePort=30000 \
  --set prometheus.service.type=NodePort \
  --set prometheus.service.nodePort=30001 \
  --set alertmanager.service.type=NodePort \
  --set alertmanager.service.nodePort=30002

echo "✅ Monitoring stack installed!"
echo ""
echo "🌐 Access URLs:"
echo "  Grafana: http://localhost:30000 (admin/admin123)"
echo "  Prometheus: http://localhost:30001"
echo "  Alertmanager: http://localhost:30002"
echo ""
echo "📊 Wait for pods to be ready:"
echo "  kubectl get pods -n monitoring"
echo ""
echo "🔍 Check services:"
echo "  kubectl get services -n monitoring"

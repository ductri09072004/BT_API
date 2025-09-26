#!/bin/bash
# Script deploy monitoring cho BT_API

echo "🔧 Deploying BT_API Monitoring..."

# Cài đặt monitoring stack
bash install-monitoring.sh

# Đợi pods ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s

# Import dashboard
echo "📊 Importing BT_API Dashboard..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d @bt-api-dashboard.json \
  http://admin:admin123@localhost:30000/api/dashboards/db

echo ""
echo "🎉 Monitoring deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Access Grafana: http://localhost:30000 (admin/admin123)"
echo "2. Check Prometheus: http://localhost:30001"
echo "3. View BT_API Dashboard in Grafana"
echo ""
echo "🔍 Useful commands:"
echo "  kubectl get pods -n monitoring"
echo "  kubectl get services -n monitoring"
echo "  kubectl port-forward -n monitoring svc/prometheus-grafana 30000:80"

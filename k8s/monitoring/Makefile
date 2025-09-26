# Monitoring Makefile for BT_API

.PHONY: install deploy status logs clean

# Cài đặt monitoring stack
install:
	@echo "🚀 Installing Prometheus + Grafana..."
	@bash install-monitoring.sh

# Deploy full monitoring với dashboard
deploy:
	@echo "🔧 Deploying complete monitoring stack..."
	@bash deploy-monitoring.sh

# Kiểm tra trạng thái monitoring
status:
	@echo "📊 Monitoring Status:"
	@kubectl get pods -n monitoring
	@echo ""
	@kubectl get services -n monitoring

# Xem logs Grafana
logs:
	@kubectl logs -f deployment/prometheus-grafana -n monitoring

# Port forward để truy cập local
port-forward:
	@echo "🌐 Starting port forwarding..."
	@echo "Grafana: http://localhost:30000"
	@echo "Prometheus: http://localhost:30001"
	@kubectl port-forward -n monitoring svc/prometheus-grafana 30000:80 &
	@kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 30001:9090 &

# Xóa monitoring stack
clean:
	@echo "🧹 Cleaning up monitoring stack..."
	@helm uninstall prometheus -n monitoring
	@kubectl delete namespace monitoring

# Kiểm tra metrics từ services
metrics:
	@echo "📈 BT_API Services Metrics:"
	@kubectl top pods -n bt-api
	@echo ""
	@kubectl top nodes

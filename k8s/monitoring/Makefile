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

# Import a dashboard from grafana.com (ID 11835)
import-11835:
	@echo "📥 Importing Grafana.com dashboard ID 11835..."
	@python3 import-grafana-11835.py
	@echo "✅ Done. Open Grafana to view the dashboard."

# Import dashboard by arbitrary Grafana.com ID: make import-id ID=12345
import-id:
	@if [ -z "$(ID)" ]; then echo "Usage: make import-id ID=12345"; exit 1; fi
	@echo "📥 Importing Grafana.com dashboard ID $(ID)..."
	@python3 import-grafana.py --id $(ID)
	@echo "✅ Done. Open Grafana to view the dashboard."

# Generate and import service traffic dashboard from local metrics
service-traffic:
	@echo "🛠️ Generating service traffic dashboard..."
	@python3 generate-service-traffic-dashboard.py
	@echo "📥 Importing dashboard into Grafana..."
	@python3 import-service-traffic.py
	@echo "✅ Service traffic dashboard imported."

# Normalize and import user-provided service traffic dashboard JSON
service-traffic-normalize:
	@echo "🔧 Normalizing bt-api-service-traffic.json to match local metrics..."
	@python3 normalize-and-import-service-traffic.py
	@echo "✅ Normalized dashboard imported."

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




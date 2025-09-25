# Kubernetes Management Makefile for BT-API Monorepo

.PHONY: help deploy undeploy status build-push logs clean

# Default target
help:
	@echo "🚀 Kubernetes Management Commands:"
	@echo ""
	@echo "📦 Deployment:"
	@echo "  make deploy                    - Deploy all services to Kubernetes"
	@echo "  make undeploy                  - Remove all services from Kubernetes"
	@echo "  make status                    - Check status of all services"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make build-push                - Build and push Docker images"
	@echo "  make build-push REGISTRY=<registry> TAG=<tag>"
	@echo ""
	@echo "🔍 Monitoring:"
	@echo "  make logs                      - Show logs for all services"
	@echo "  make logs SERVICE=<service>   - Show logs for specific service"
	@echo "  make clean                     - Clean up resources"
	@echo ""
	@echo "📋 Examples:"
	@echo "  make deploy"
	@echo "  make build-push REGISTRY=myregistry.com TAG=v1.0.0"
	@echo "  make logs SERVICE=payment-service"

# Deploy all services
deploy:
	@echo "🚀 Deploying BT-API to Kubernetes..."
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh

# Undeploy all services
undeploy:
	@echo "🗑️ Removing BT-API from Kubernetes..."
	@chmod +x scripts/undeploy.sh
	@./scripts/undeploy.sh

# Check status
status:
	@echo "📊 Checking BT-API status..."
	@chmod +x scripts/status.sh
	@./scripts/status.sh

# Build and push images
build-push:
	@echo "🐳 Building and pushing Docker images..."
	@chmod +x scripts/build-and-push.sh
	@./scripts/build-and-push.sh $(REGISTRY) $(TAG)

# Show logs
logs:
	@if [ -z "$(SERVICE)" ]; then \
		echo "📋 Showing logs for all services..."; \
		kubectl logs -n bt-api -l app=health-service --tail=10; \
		kubectl logs -n bt-api -l app=hello-service --tail=10; \
		kubectl logs -n bt-api -l app=admin-service --tail=10; \
		kubectl logs -n bt-api -l app=dynamic-service --tail=10; \
		kubectl logs -n bt-api -l app=payment-service --tail=10; \
	else \
		echo "📋 Showing logs for $(SERVICE)..."; \
		kubectl logs -n bt-api -l app=$(SERVICE) --tail=20; \
	fi

# Clean up
clean:
	@echo "🧹 Cleaning up resources..."
	@kubectl delete namespace bt-api --ignore-not-found=true
	@echo "✅ Cleanup completed"

# Port forward for local testing
port-forward:
	@echo "🔗 Setting up port forwarding..."
	@echo "Health: http://localhost:8001"
	@echo "Hello: http://localhost:8002"
	@echo "Admin: http://localhost:8003"
	@echo "Dynamic: http://localhost:8004"
	@echo "Payment: http://localhost:8009"
	@kubectl port-forward -n bt-api service/health-service 8001:8000 &
	@kubectl port-forward -n bt-api service/hello-service 8002:8000 &
	@kubectl port-forward -n bt-api service/admin-service 8003:8000 &
	@kubectl port-forward -n bt-api service/dynamic-service 8004:8000 &
	@kubectl port-forward -n bt-api service/payment-service 8009:8000 &
	@echo "✅ Port forwarding started. Press Ctrl+C to stop."

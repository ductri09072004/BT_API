# Kafka Management Makefile for BT_API

.PHONY: help start stop restart setup topics logs clean status

# Default target
help:
	@echo "Kafka Management Commands:"
	@echo "  make start     - Start Kafka infrastructure"
	@echo "  make stop      - Stop Kafka infrastructure"
	@echo "  make restart   - Restart Kafka infrastructure"
	@echo "  make setup     - Full setup (start + create topics)"
	@echo "  make topics    - Create Kafka topics"
	@echo "  make logs      - Show Kafka logs"
	@echo "  make status    - Show Kafka status"
	@echo "  make clean     - Clean up Kafka data"

# Start Kafka infrastructure
start:
	@echo "🚀 Starting Kafka infrastructure..."
	docker-compose -f docker-compose-kafka.yml up -d
	@echo "⏳ Waiting for Kafka to be ready..."
	@sleep 30
	@echo "✅ Kafka infrastructure started!"

# Stop Kafka infrastructure
stop:
	@echo "🛑 Stopping Kafka infrastructure..."
	docker-compose -f docker-compose-kafka.yml down

# Restart Kafka infrastructure
restart: stop start

# Setup topics
topics:
	@echo "📝 Creating Kafka topics..."
	@./setup-topics.sh

# Full setup
setup: start topics
	@echo "✅ Kafka setup complete!"
	@echo "🌐 Kafka UI: http://localhost:8080"

# Show logs
logs:
	docker-compose -f docker-compose-kafka.yml logs -f

# Show status
status:
	@echo "📊 Kafka Status:"
	@docker-compose -f docker-compose-kafka.yml ps
	@echo ""
	@echo "📝 Available topics:"
	@docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list 2>/dev/null || echo "Kafka not running"

# Clean up
clean:
	@echo "🧹 Cleaning up Kafka data..."
	docker-compose -f docker-compose-kafka.yml down -v
	docker system prune -f

# Start consumers
consumers:
	@echo "🔄 Starting Kafka consumers..."
	docker-compose up -d grafana-consumer kibana-consumer
	@echo "✅ Consumers started!"

# Stop consumers
stop-consumers:
	@echo "🛑 Stopping Kafka consumers..."
	docker-compose stop grafana-consumer kibana-consumer

# Show consumer logs
consumer-logs:
	docker-compose logs -f grafana-consumer kibana-consumer



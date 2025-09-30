#!/bin/bash

echo "🚀 Setting up Kafka for BT_API Monitoring Pipeline..."

# Create kafka directory if it doesn't exist
mkdir -p kafka

# Start Kafka infrastructure
echo "📦 Starting Kafka infrastructure..."
docker-compose -f kafka/docker-compose-kafka.yml up -d

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
sleep 30

# Setup topics
echo "📝 Setting up Kafka topics..."
./kafka/setup-topics.sh

echo ""
echo "✅ Kafka setup complete!"
echo ""
echo "🌐 Available services:"
echo "   - Kafka UI: http://localhost:8080"
echo "   - Kafka Bootstrap: host.docker.internal:9092"
echo "   - Zookeeper: localhost:2181"
echo ""
echo "📊 Topics created:"
echo "   - metrics.events (for Grafana)"
echo "   - logs.events (for Kibana)"
echo "   - health.events (for health checks)"
echo "   - order.events, customer.events, employee.events, driver.events"
echo ""
echo "🔄 Next steps:"
echo "   1. Start your services: docker-compose up -d"
echo "   2. Start Kafka consumers: docker-compose up -d grafana-consumer kibana-consumer"
echo "   3. Access Grafana: http://localhost:3000"
echo "   4. Access Kibana: http://localhost:5601"

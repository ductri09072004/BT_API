#!/bin/bash

# Kafka Topics Setup Script
echo "🚀 Setting up Kafka topics for BT_API monitoring..."

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
until docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list > /dev/null 2>&1; do
    echo "Waiting for Kafka..."
    sleep 5
done

echo "✅ Kafka is ready!"

# Create topics from JSON configuration
echo "📝 Creating topics..."

# Metrics topic
docker exec bt-api-kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic metrics.events \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete \
  --config compression.type=snappy \
  --if-not-exists

# Logs topic
docker exec bt-api-kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic logs.events \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete \
  --config compression.type=snappy \
  --if-not-exists

# Health topic
docker exec bt-api-kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic health.events \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=86400000 \
  --config cleanup.policy=delete \
  --if-not-exists

# Service-specific topics
services=("order" "customer" "employee" "driver")

for service in "${services[@]}"; do
    echo "📝 Creating topic: ${service}.events"
    docker exec bt-api-kafka kafka-topics \
      --bootstrap-server localhost:29092 \
      --create \
      --topic ${service}.events \
      --partitions 2 \
      --replication-factor 1 \
      --config retention.ms=2592000000 \
      --config cleanup.policy=delete \
      --if-not-exists
done

echo "✅ All topics created successfully!"
echo ""
echo "📊 Available topics:"
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list

echo ""
echo "🎉 Kafka setup complete!"
echo "🌐 Kafka UI: http://localhost:8080"
echo "📡 Kafka Bootstrap: host.docker.internal:9092"

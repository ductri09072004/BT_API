Write-Host "🚀 Starting Kafka infrastructure..." -ForegroundColor Green
docker-compose -f docker-compose-kafka.yml up -d

Write-Host "⏳ Waiting for Kafka to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "📝 Creating Kafka topics..." -ForegroundColor Cyan

# Create topics
Write-Host "📝 Creating topic: metrics.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic metrics.events --partitions 3 --replication-factor 1 --config retention.ms=604800000 --config cleanup.policy=delete --if-not-exists

Write-Host "📝 Creating topic: logs.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic logs.events --partitions 3 --replication-factor 1 --config retention.ms=2592000000 --config cleanup.policy=delete --if-not-exists

Write-Host "📝 Creating topic: health.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic health.events --partitions 1 --replication-factor 1 --config retention.ms=86400000 --config cleanup.policy=delete --if-not-exists

Write-Host "📝 Creating topic: order.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic order.events --partitions 2 --replication-factor 1 --config retention.ms=2592000000 --config cleanup.policy=delete --if-not-exists

Write-Host "📝 Creating topic: customer.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic customer.events --partitions 2 --replication-factor 1 --config retention.ms=2592000000 --config cleanup.policy=delete --if-not-exists

Write-Host "📝 Creating topic: employee.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic employee.events --partitions 2 --replication-factor 1 --config retention.ms=2592000000 --config cleanup.policy=delete --if-not-exists

Write-Host "📝 Creating topic: driver.events" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic driver.events --partitions 2 --replication-factor 1 --config retention.ms=2592000000 --config cleanup.policy=delete --if-not-exists

Write-Host "✅ All topics created successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "📊 Available topics:" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list

Write-Host ""
Write-Host "✅ Kafka setup complete!" -ForegroundColor Green
Write-Host "🌐 Kafka UI: http://localhost:8080" -ForegroundColor Cyan
Write-Host "📡 Kafka Bootstrap: host.docker.internal:9092" -ForegroundColor Cyan



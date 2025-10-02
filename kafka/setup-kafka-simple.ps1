# Simple Kafka Setup Script for Windows PowerShell

Write-Host "🚀 Starting Kafka infrastructure..." -ForegroundColor Green
docker-compose -f docker-compose-kafka.yml up -d

Write-Host "⏳ Waiting for Kafka to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "📝 Creating Kafka topics..." -ForegroundColor Cyan

# Wait for Kafka to be ready
do {
    try {
        docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list | Out-Null
        $kafkaReady = $true
    } catch {
        $kafkaReady = $false
        Write-Host "Waiting for Kafka..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
} while (-not $kafkaReady)

Write-Host "✅ Kafka is ready!" -ForegroundColor Green

# Create topics
$topics = @(
    @{Name="metrics.events"; Partitions=3; Retention="604800000"},
    @{Name="logs.events"; Partitions=3; Retention="2592000000"},
    @{Name="health.events"; Partitions=1; Retention="86400000"},
    @{Name="order.events"; Partitions=2; Retention="2592000000"},
    @{Name="customer.events"; Partitions=2; Retention="2592000000"},
    @{Name="employee.events"; Partitions=2; Retention="2592000000"},
    @{Name="driver.events"; Partitions=2; Retention="2592000000"}
)

foreach ($topic in $topics) {
    Write-Host "📝 Creating topic: $($topic.Name)" -ForegroundColor Cyan
    docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --create --topic $topic.Name --partitions $topic.Partitions --replication-factor 1 --config retention.ms=$topic.Retention --config cleanup.policy=delete --if-not-exists
}

Write-Host "✅ All topics created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Available topics:" -ForegroundColor Cyan
docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list

Write-Host ""
Write-Host "✅ Kafka setup complete!" -ForegroundColor Green
Write-Host "🌐 Kafka UI: http://localhost:8080" -ForegroundColor Cyan
Write-Host "📡 Kafka Bootstrap: host.docker.internal:9092" -ForegroundColor Cyan



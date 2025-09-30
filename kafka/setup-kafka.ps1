# Kafka Setup Script for Windows PowerShell
param(
    [switch]$Help,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Setup,
    [switch]$Topics,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Clean,
    [switch]$Consumers,
    [switch]$StopConsumers
)

function Show-Help {
    Write-Host "Kafka Management Commands:" -ForegroundColor Green
    Write-Host "  .\setup-kafka.ps1 -Start       - Start Kafka infrastructure" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Stop        - Stop Kafka infrastructure" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Restart     - Restart Kafka infrastructure" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Setup       - Full setup (start + create topics)" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Topics      - Create Kafka topics" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Logs        - Show Kafka logs" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Status      - Show Kafka status" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Clean       - Clean up Kafka data" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -Consumers   - Start Kafka consumers" -ForegroundColor Yellow
    Write-Host "  .\setup-kafka.ps1 -StopConsumers - Stop Kafka consumers" -ForegroundColor Yellow
}

function Start-Kafka {
    Write-Host "🚀 Starting Kafka infrastructure..." -ForegroundColor Green
    docker-compose -f docker-compose-kafka.yml up -d
    Write-Host "⏳ Waiting for Kafka to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    Write-Host "✅ Kafka infrastructure started!" -ForegroundColor Green
}

function Stop-Kafka {
    Write-Host "🛑 Stopping Kafka infrastructure..." -ForegroundColor Red
    docker-compose -f docker-compose-kafka.yml down
}

function Restart-Kafka {
    Stop-Kafka
    Start-Kafka
}

function Setup-Topics {
    Write-Host "📝 Creating Kafka topics..." -ForegroundColor Cyan
    if (Test-Path "setup-topics.sh") {
        # Use WSL or Git Bash if available
        if (Get-Command wsl -ErrorAction SilentlyContinue) {
            wsl bash setup-topics.sh
        } elseif (Get-Command bash -ErrorAction SilentlyContinue) {
            bash setup-topics.sh
        } else {
            # Fallback to manual topic creation
            Write-Host "⚠️  Bash not found, creating topics manually..." -ForegroundColor Yellow
            Create-Topics-Manually
        }
    } else {
        Write-Host "❌ setup-topics.sh not found!" -ForegroundColor Red
    }
}

function Create-Topics-Manually {
    Write-Host "📝 Creating topics manually..." -ForegroundColor Cyan
    
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
        docker exec bt-api-kafka kafka-topics `
            --bootstrap-server localhost:29092 `
            --create `
            --topic $topic.Name `
            --partitions $topic.Partitions `
            --replication-factor 1 `
            --config retention.ms=$topic.Retention `
            --config cleanup.policy=delete `
            --if-not-exists
    }
    
    Write-Host "✅ All topics created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Available topics:" -ForegroundColor Cyan
    docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list
}

function Show-Logs {
    docker-compose -f docker-compose-kafka.yml logs -f
}

function Show-Status {
    Write-Host "📊 Kafka Status:" -ForegroundColor Cyan
    docker-compose -f docker-compose-kafka.yml ps
    Write-Host ""
    Write-Host "📝 Available topics:" -ForegroundColor Cyan
    try {
        docker exec bt-api-kafka kafka-topics --bootstrap-server localhost:29092 --list
    } catch {
        Write-Host "Kafka not running" -ForegroundColor Red
    }
}

function Clean-Kafka {
    Write-Host "🧹 Cleaning up Kafka data..." -ForegroundColor Red
    docker-compose -f docker-compose-kafka.yml down -v
    docker system prune -f
}

function Start-Consumers {
    Write-Host "🔄 Starting Kafka consumers..." -ForegroundColor Green
    docker-compose up -d grafana-consumer kibana-consumer
    Write-Host "✅ Consumers started!" -ForegroundColor Green
}

function Stop-Consumers {
    Write-Host "🛑 Stopping Kafka consumers..." -ForegroundColor Red
    docker-compose stop grafana-consumer kibana-consumer
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

if ($Setup) {
    Start-Kafka
    Setup-Topics
    Write-Host ""
    Write-Host "✅ Kafka setup complete!" -ForegroundColor Green
    Write-Host "🌐 Kafka UI: http://localhost:8080" -ForegroundColor Cyan
    exit 0
}

if ($Start) {
    Start-Kafka
    exit 0
}

if ($Stop) {
    Stop-Kafka
    exit 0
}

if ($Restart) {
    Restart-Kafka
    exit 0
}

if ($Topics) {
    Setup-Topics
    exit 0
}

if ($Logs) {
    Show-Logs
    exit 0
}

if ($Status) {
    Show-Status
    exit 0
}

if ($Clean) {
    Clean-Kafka
    exit 0
}

if ($Consumers) {
    Start-Consumers
    exit 0
}

if ($StopConsumers) {
    Stop-Consumers
    exit 0
}

# If no parameters, show help
Show-Help

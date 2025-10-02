# 🚀 Kafka Monitoring Pipeline for BT_API

Hệ thống Kafka được thiết kế để giảm tải cho các services và tạo ra pipeline hiệu quả cho monitoring với Grafana và Kibana.

## 🏗️ Architecture

```
Services → Kafka Topics → Consumers → Grafana/Kibana
    ↓           ↓           ↓
  Metrics    Events     Logs
```

### Topics:
- `metrics.events` - Metrics cho Grafana
- `logs.events` - Logs cho Kibana  
- `health.events` - Health checks
- `{service}.events` - Business events (order, customer, employee, driver)

## 🚀 Quick Start

### 1. Setup Kafka Infrastructure
```bash
# Start Kafka
make setup

# Hoặc manual:
docker-compose -f docker-compose-kafka.yml up -d
./setup-topics.sh
```

### 2. Start Services với Kafka
```bash
# Start all services
docker-compose up -d

# Start Kafka consumers
make consumers
```

### 3. Access Services
- **Kafka UI**: http://localhost:8080
- **Grafana**: http://localhost:3000  
- **Kibana**: http://localhost:5601
- **Prometheus**: http://localhost:9090

## 📊 Benefits

### ✅ Reduced Service Load
- Services chỉ cần publish metrics/logs tới Kafka
- Không cần direct connection tới Prometheus/Elasticsearch
- Async processing giảm latency

### ✅ Scalability
- Multiple consumers có thể process cùng data
- Easy horizontal scaling
- Fault tolerance với Kafka replication

### ✅ Flexibility
- Dễ dàng thêm consumers mới
- Support multiple monitoring systems
- Data retention policies

## 🔧 Management Commands

```bash
# Kafka Infrastructure
make start          # Start Kafka
make stop           # Stop Kafka  
make restart        # Restart Kafka
make setup          # Full setup
make topics         # Create topics only
make logs           # Show logs
make status         # Show status
make clean          # Clean up data

# Consumers
make consumers      # Start consumers
make stop-consumers # Stop consumers
make consumer-logs  # Show consumer logs
```

## 📝 Configuration

### Environment Variables
```bash
KAFKA_BOOTSTRAP=host.docker.internal:9092
ELASTICSEARCH_HOST=host.docker.internal:9200
```

### Topics Configuration
Topics được config trong `topics.json`:
- **Partitions**: 3 cho metrics/logs, 2 cho events
- **Retention**: 7 days cho metrics, 30 days cho events
- **Compression**: Snappy cho performance

## 🔍 Monitoring

### Metrics Flow
1. **Service** → Publishes metrics to `metrics.events`
2. **Grafana Consumer** → Consumes metrics, exposes Prometheus format
3. **Prometheus** → Scrapes from consumer port 9090
4. **Grafana** → Queries Prometheus

### Logs Flow  
1. **Service** → Publishes logs to `logs.events`
2. **Kibana Consumer** → Consumes logs, indexes to Elasticsearch
3. **Kibana** → Queries Elasticsearch

## 🛠️ Development

### Adding New Service
1. Add service to `docker-compose.yml`
2. Add Kafka environment variables
3. Import `producer.py` in service
4. Use `send_metric()`, `send_log()`, `send_event()`

### Custom Consumers
1. Create consumer script in `kafka/` directory
2. Add to `docker-compose.yml`
3. Implement consumer logic

## 🐛 Troubleshooting

### Kafka Not Starting
```bash
# Check logs
make logs

# Check ports
netstat -tlnp | grep 9092

# Clean restart
make clean && make setup
```

### Consumers Not Working
```bash
# Check consumer logs
make consumer-logs

# Check topics
make status

# Restart consumers
make stop-consumers && make consumers
```

### Metrics Not Appearing
1. Check service logs for Kafka errors
2. Verify topics exist: `make status`
3. Check consumer status: `make consumer-logs`
4. Verify Prometheus config

## 📈 Performance Tuning

### Kafka Tuning
- Adjust `KAFKA_NUM_PARTITIONS` for parallelism
- Tune `KAFKA_LOG_RETENTION_HOURS` for storage
- Configure `KAFKA_LOG_SEGMENT_BYTES` for performance

### Consumer Tuning
- Adjust `scrape_interval` in Prometheus
- Tune batch sizes in consumers
- Configure connection pools

## 🔐 Security

### Production Considerations
- Enable SSL/TLS for Kafka
- Configure authentication/authorization
- Use secrets management
- Network isolation
- Resource limits

## 📚 References

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Prometheus Client](https://github.com/prometheus/client_python)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [FastAPI](https://fastapi.tiangolo.com/)



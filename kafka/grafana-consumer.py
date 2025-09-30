#!/usr/bin/env python3
"""
Kafka Consumer for Grafana Metrics
Consumes metrics from Kafka and forwards to Prometheus-compatible format
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any
from aiokafka import AIOKafkaConsumer
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
metrics_received_total = Counter('kafka_metrics_received_total', 'Total metrics received from Kafka', ['service', 'metric_name'])
metrics_processing_duration = Histogram('kafka_metrics_processing_duration_seconds', 'Time spent processing metrics')
service_metrics = {}  # Dynamic metrics storage

class GrafanaKafkaConsumer:
    """Kafka Consumer for Grafana metrics"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
        self.consumer: AIOKafkaConsumer = None
        self.is_running = False
        
    async def start(self):
        """Start Kafka consumer"""
        try:
            self.consumer = AIOKafkaConsumer(
                'metrics.events',
                'health.events',
                bootstrap_servers=self.bootstrap_servers,
                group_id='grafana-consumer',
                enable_auto_commit=True,
                auto_offset_reset='latest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            await self.consumer.start()
            self.is_running = True
            logger.info("🚀 Grafana Kafka Consumer started")
            
            # Start Prometheus metrics server
            start_http_server(9091)
            logger.info("📊 Prometheus metrics server started on port 9091")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Kafka consumer: {e}")
            raise
    
    async def stop(self):
        """Stop Kafka consumer"""
        if self.consumer:
            await self.consumer.stop()
            self.is_running = False
            logger.info("🛑 Grafana Kafka Consumer stopped")
    
    def create_or_get_metric(self, service: str, metric_name: str, metric_type: str):
        """Create or get Prometheus metric"""
        key = f"{service}_{metric_name}"
        
        if key not in service_metrics:
            if metric_type == 'counter':
                service_metrics[key] = Counter(
                    f'{service}_{metric_name}_total',
                    f'Kafka metric: {service}.{metric_name}',
                    ['service', 'labels']
                )
            elif metric_type == 'histogram':
                service_metrics[key] = Histogram(
                    f'{service}_{metric_name}_seconds',
                    f'Kafka metric: {service}.{metric_name}',
                    ['service', 'labels']
                )
            else:  # gauge
                service_metrics[key] = Gauge(
                    f'{service}_{metric_name}',
                    f'Kafka metric: {service}.{metric_name}',
                    ['service', 'labels']
                )
        
        return service_metrics[key]
    
    async def process_metric(self, data: Dict[str, Any]):
        """Process metric data"""
        start_time = time.time()
        
        try:
            service = data.get('service')
            metric_name = data.get('metric_name')
            value = data.get('value')
            labels = data.get('labels', {})
            
            if not all([service, metric_name, value is not None]):
                logger.warning(f"Incomplete metric data: {data}")
                return
            
            # Determine metric type based on name
            if 'total' in metric_name or 'count' in metric_name:
                metric_type = 'counter'
            elif 'duration' in metric_name or 'latency' in metric_name:
                metric_type = 'histogram'
            else:
                metric_type = 'gauge'
            
            # Create or get metric
            metric = self.create_or_get_metric(service, metric_name, metric_type)
            
            # Update metric
            labels_str = ','.join([f"{k}={v}" for k, v in labels.items()])
            
            if metric_type == 'counter':
                metric.labels(service=service, labels=labels_str).inc(value)
            elif metric_type == 'histogram':
                metric.labels(service=service, labels=labels_str).observe(value)
            else:  # gauge
                metric.labels(service=service, labels=labels_str).set(value)
            
            # Update metrics counter
            metrics_received_total.labels(service=service, metric_name=metric_name).inc()
            
        except Exception as e:
            logger.error(f"Error processing metric: {e}")
        finally:
            metrics_processing_duration.observe(time.time() - start_time)
    
    async def process_health_check(self, data: Dict[str, Any]):
        """Process health check data"""
        try:
            service = data.get('service')
            status = data.get('status')
            details = data.get('details', {})
            
            # Create health metric
            health_metric = self.create_or_get_metric(service, 'health_status', 'gauge')
            health_value = 1 if status == 'healthy' else 0
            health_metric.labels(service=service, labels='').set(health_value)
            
            logger.info(f"Health check: {service} = {status}")
            
        except Exception as e:
            logger.error(f"Error processing health check: {e}")
    
    async def consume_loop(self):
        """Main consumption loop"""
        logger.info("🔄 Starting consumption loop...")
        
        try:
            async for message in self.consumer:
                try:
                    data = message.value
                    data_type = data.get('type')
                    
                    if data_type == 'metric':
                        await self.process_metric(data)
                    elif data_type == 'health':
                        await self.process_health_check(data)
                    else:
                        logger.warning(f"Unknown data type: {data_type}")
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Consumption loop cancelled")
        except Exception as e:
            logger.error(f"Error in consumption loop: {e}")
    
    async def run(self):
        """Run the consumer"""
        await self.start()
        try:
            await self.consume_loop()
        finally:
            await self.stop()

async def main():
    """Main function"""
    consumer = GrafanaKafkaConsumer()
    try:
        await consumer.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

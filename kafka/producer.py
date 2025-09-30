#!/usr/bin/env python3
"""
Kafka Producer utility for BT_API services
Handles metrics, logs, and events publishing to Kafka topics
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaProducer:
    """Kafka Producer for BT_API services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP", "host.docker.internal:9092")
        self.producer: Optional[AIOKafkaProducer] = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to Kafka"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                compression_type='snappy',
                acks='all',
                retries=3,
                retry_backoff_ms=100
            )
            await self.producer.start()
            self.is_connected = True
            logger.info(f"✅ {self.service_name} Kafka Producer connected")
        except Exception as e:
            logger.error(f"❌ Failed to connect Kafka Producer: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from Kafka"""
        if self.producer:
            await self.producer.stop()
            self.is_connected = False
            logger.info(f"🔌 {self.service_name} Kafka Producer disconnected")
    
    async def send_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Send metric to Kafka"""
        if not self.is_connected:
            logger.warning("Kafka Producer not connected, skipping metric")
            return
        
        metric_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "metric_name": metric_name,
            "value": value,
            "labels": labels or {},
            "type": "metric"
        }
        
        try:
            await self.producer.send(
                'metrics.events',
                value=metric_data,
                key=f"{self.service_name}.{metric_name}"
            )
        except KafkaError as e:
            logger.error(f"Failed to send metric: {e}")
    
    async def send_log(self, level: str, message: str, extra: Dict[str, Any] = None):
        """Send log to Kafka"""
        if not self.is_connected:
            logger.warning("Kafka Producer not connected, skipping log")
            return
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            "extra": extra or {},
            "type": "log"
        }
        
        try:
            await self.producer.send(
                'logs.events',
                value=log_data,
                key=f"{self.service_name}.logs"
            )
        except KafkaError as e:
            logger.error(f"Failed to send log: {e}")
    
    async def send_event(self, event_type: str, data: Dict[str, Any]):
        """Send business event to Kafka"""
        if not self.is_connected:
            logger.warning("Kafka Producer not connected, skipping event")
            return
        
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "data": data,
            "type": "event"
        }
        
        topic = f"{self.service_name}.events"
        
        try:
            await self.producer.send(
                topic,
                value=event_data,
                key=f"{self.service_name}.{event_type}"
            )
        except KafkaError as e:
            logger.error(f"Failed to send event: {e}")
    
    async def send_health_check(self, status: str, details: Dict[str, Any] = None):
        """Send health check to Kafka"""
        if not self.is_connected:
            logger.warning("Kafka Producer not connected, skipping health check")
            return
        
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "status": status,
            "details": details or {},
            "type": "health"
        }
        
        try:
            await self.producer.send(
                'health.events',
                value=health_data,
                key=f"{self.service_name}.health"
            )
        except KafkaError as e:
            logger.error(f"Failed to send health check: {e}")

# Global producer instance
_kafka_producer: Optional[KafkaProducer] = None

def get_kafka_producer(service_name: str) -> KafkaProducer:
    """Get or create Kafka producer instance"""
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducer(service_name)
    return _kafka_producer

# Convenience functions
async def send_metric(service_name: str, metric_name: str, value: float, labels: Dict[str, str] = None):
    """Send metric to Kafka"""
    producer = get_kafka_producer(service_name)
    await producer.send_metric(metric_name, value, labels)

async def send_log(service_name: str, level: str, message: str, extra: Dict[str, Any] = None):
    """Send log to Kafka"""
    producer = get_kafka_producer(service_name)
    await producer.send_log(level, message, extra)

async def send_event(service_name: str, event_type: str, data: Dict[str, Any]):
    """Send business event to Kafka"""
    producer = get_kafka_producer(service_name)
    await producer.send_event(event_type, data)

async def send_health_check(service_name: str, status: str, details: Dict[str, Any] = None):
    """Send health check to Kafka"""
    producer = get_kafka_producer(service_name)
    await producer.send_health_check(status, details)

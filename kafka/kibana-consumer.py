#!/usr/bin/env python3
"""
Kafka Consumer for Kibana/Elasticsearch
Consumes logs and events from Kafka and forwards to Elasticsearch
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any
from aiokafka import AIOKafkaConsumer
from elasticsearch import AsyncElasticsearch
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KibanaKafkaConsumer:
    """Kafka Consumer for Kibana/Elasticsearch"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
        self.consumer: AIOKafkaConsumer = None
        self.elasticsearch: AsyncElasticsearch = None
        self.is_running = False
        
    async def start(self):
        """Start Kafka consumer and Elasticsearch client"""
        try:
            # Start Kafka consumer
            self.consumer = AIOKafkaConsumer(
                'logs.events',
                'order.events',
                'customer.events',
                'employee.events',
                'driver.events',
                bootstrap_servers=self.bootstrap_servers,
                group_id='kibana-consumer',
                enable_auto_commit=True,
                auto_offset_reset='latest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            await self.consumer.start()
            logger.info("🚀 Kibana Kafka Consumer started")
            
            # Start Elasticsearch client
            self.elasticsearch = AsyncElasticsearch(
                [f"http://{self.elasticsearch_host}"],
                verify_certs=False,
                request_timeout=30
            )
            
            # Test Elasticsearch connection
            info = await self.elasticsearch.info()
            logger.info(f"✅ Connected to Elasticsearch: {info['version']['number']}")
            
            self.is_running = True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Kibana consumer: {e}")
            raise
    
    async def stop(self):
        """Stop Kafka consumer and Elasticsearch client"""
        if self.consumer:
            await self.consumer.stop()
            logger.info("🛑 Kibana Kafka Consumer stopped")
        
        if self.elasticsearch:
            await self.elasticsearch.close()
            logger.info("🔌 Elasticsearch client closed")
        
        self.is_running = False
    
    def get_index_name(self, data_type: str, service: str = None) -> str:
        """Get Elasticsearch index name"""
        timestamp = datetime.utcnow().strftime("%Y.%m.%d")
        
        if data_type == 'log':
            return f"bt-api-logs-{timestamp}"
        elif data_type == 'event':
            return f"bt-api-{service}-events-{timestamp}"
        else:
            return f"bt-api-{data_type}-{timestamp}"
    
    async def index_to_elasticsearch(self, data: Dict[str, Any]):
        """Index data to Elasticsearch"""
        try:
            data_type = data.get('type')
            service = data.get('service')
            
            # Add additional metadata
            data['@timestamp'] = data.get('timestamp', datetime.utcnow().isoformat())
            data['kafka_topic'] = 'unknown'  # Will be set by consumer
            
            index_name = self.get_index_name(data_type, service)
            
            # Create index if it doesn't exist
            if not await self.elasticsearch.indices.exists(index=index_name):
                await self.create_index_template(index_name, data_type)
            
            # Index the document
            response = await self.elasticsearch.index(
                index=index_name,
                body=data
            )
            
            logger.debug(f"Indexed document: {response['_id']}")
            
        except Exception as e:
            logger.error(f"Error indexing to Elasticsearch: {e}")
    
    async def create_index_template(self, index_name: str, data_type: str):
        """Create index with proper mapping"""
        try:
            mapping = {
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "timestamp": {"type": "date"},
                        "service": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "kafka_topic": {"type": "keyword"}
                    }
                }
            }
            
            if data_type == 'log':
                mapping["mappings"]["properties"].update({
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "extra": {"type": "object"}
                })
            elif data_type == 'event':
                mapping["mappings"]["properties"].update({
                    "event_type": {"type": "keyword"},
                    "data": {"type": "object"}
                })
            
            await self.elasticsearch.indices.create(
                index=index_name,
                body=mapping
            )
            
            logger.info(f"Created index: {index_name}")
            
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
    
    async def process_log(self, data: Dict[str, Any]):
        """Process log data"""
        try:
            logger.info(f"Log from {data.get('service')}: {data.get('level')} - {data.get('message')}")
            await self.index_to_elasticsearch(data)
            
        except Exception as e:
            logger.error(f"Error processing log: {e}")
    
    async def process_event(self, data: Dict[str, Any]):
        """Process event data"""
        try:
            service = data.get('service')
            event_type = data.get('event_type')
            logger.info(f"Event from {service}: {event_type}")
            await self.index_to_elasticsearch(data)
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    async def consume_loop(self):
        """Main consumption loop"""
        logger.info("🔄 Starting consumption loop...")
        
        try:
            async for message in self.consumer:
                try:
                    data = message.value
                    data['kafka_topic'] = message.topic
                    
                    data_type = data.get('type')
                    
                    if data_type == 'log':
                        await self.process_log(data)
                    elif data_type == 'event':
                        await self.process_event(data)
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
    consumer = KibanaKafkaConsumer()
    try:
        await consumer.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

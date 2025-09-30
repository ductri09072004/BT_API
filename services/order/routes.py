from fastapi import APIRouter, HTTPException, Body
from db import db

router = APIRouter()


@router.get("/orders")
async def get_orders():
    if db is None:
        raise HTTPException(status_code=500, detail="MONGODB_URI is not configured")
    docs = await db.Order.find().to_list(length=None)
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])  # serialize ObjectId
    return docs
    

# uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Prometheus metrics
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import json
from aiokafka import AIOKafkaProducer
from typing import Optional

# Metrics definitions
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# Kafka config
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "order.events")
producer: Optional[AIOKafkaProducer] = None

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.on_event("startup")
async def _start_kafka_producer():
    global producer
    try:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
        await producer.start()
    except Exception:
        producer = None


@router.on_event("shutdown")
async def _stop_kafka_producer():
    if producer:
        await producer.stop()


@router.post("/orders/event")
async def publish_order_event(payload: dict = Body(...)):
    if producer is None:
        raise HTTPException(status_code=503, detail="Kafka producer not available")
    try:
        key = str(payload.get("orderId", "")).encode() if payload.get("orderId") else None
        value = json.dumps(payload, ensure_ascii=False).encode()
        await producer.send_and_wait(KAFKA_TOPIC, value=value, key=key)
        return {"status": "published", "topic": KAFKA_TOPIC}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kafka publish error: {e}")

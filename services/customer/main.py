from fastapi import FastAPI, Request
from routes import router
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os
import asyncio
import json
from aiokafka import AIOKafkaConsumer

# Prometheus metrics (service-scoped names to avoid duplicates)
customer_http_requests_total = Counter(
    'customer_http_requests_total', 'Total HTTP requests (customer)', ['method', 'endpoint', 'status']
)
customer_http_request_duration_seconds = Histogram(
    'customer_http_request_duration_seconds', 'HTTP request duration (customer)', ['method', 'endpoint']
)

# Tạo FastAPI app
app = FastAPI(
    title="Customer",
    description="Template service for microservices",
    version="1.0.0"
)

# Kafka consumer setup
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "order.events")
consumer: AIOKafkaConsumer | None = None
consumer_task: asyncio.Task | None = None

# Middleware để track HTTP requests
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Extract metrics
    method = request.method
    endpoint = request.url.path
    status = str(response.status_code)
    
    # Update metrics
    customer_http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    customer_http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response

# Đăng ký routes KHÔNG cần API key
app.include_router(router)

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint - không yêu cầu API key"""
    from fastapi import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def _consume_loop():
    assert consumer is not None
    try:
        while True:
            msg = await consumer.getone()
            # Log đơn giản
            print("[Kafka] Received:", msg.topic, msg.key, msg.value)
    except asyncio.CancelledError:
        pass


@app.on_event("startup")
async def _start_consumer():
    global consumer, consumer_task
    try:
        consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="customer-consumer",
            enable_auto_commit=True,
            auto_offset_reset="earliest",
        )
        await consumer.start()
        consumer_task = asyncio.create_task(_consume_loop())
    except Exception:
        consumer = None
        consumer_task = None


@app.on_event("shutdown")
async def _stop_consumer():
    if consumer_task:
        consumer_task.cancel()
        with contextlib.suppress(Exception):
            await consumer_task
    if consumer:
        await consumer.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

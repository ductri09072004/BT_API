from fastapi import FastAPI, Request
from routes import router
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import os
import sys
import asyncio

# Add kafka directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../kafka'))
from producer import KafkaProducer, send_metric, send_log, send_health_check

# Prometheus metrics (service-scoped names to avoid duplicates)
order_http_requests_total = Counter(
    'order_http_requests_total', 'Total HTTP requests (order)', ['method', 'endpoint', 'status']
)
order_http_request_duration_seconds = Histogram(
    'order_http_request_duration_seconds', 'HTTP request duration (order)', ['method', 'endpoint']
)

# Tạo FastAPI app
app = FastAPI(
    title="Order",
    description="Order service for microservices",
    version="1.0.0"
)

# Kafka Producer
kafka_producer = KafkaProducer("order")

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
    order_http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    order_http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    # Send metrics to Kafka
    try:
        await send_metric("order", "http_requests_total", 1, {
            "method": method,
            "endpoint": endpoint,
            "status": status
        })
        await send_metric("order", "http_request_duration_seconds", duration, {
            "method": method,
            "endpoint": endpoint
        })
    except Exception as e:
        print(f"Failed to send metrics to Kafka: {e}")
    
    return response

# Đăng ký routes KHÔNG cần API key
app.include_router(router)

@app.get("/healthz")
async def health_check():
    # Send health check to Kafka
    try:
        await send_health_check("order", "healthy", {
            "service": "order",
            "timestamp": time.time()
        })
    except Exception as e:
        print(f"Failed to send health check to Kafka: {e}")
    
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint - không yêu cầu API key"""
    from fastapi import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer on startup"""
    await kafka_producer.connect()
    await send_log("order", "info", "Order service started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup Kafka producer on shutdown"""
    await kafka_producer.disconnect()
    await send_log("order", "info", "Order service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

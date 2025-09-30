from fastapi import FastAPI, Request
from routes import router
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Prometheus metrics (service-scoped names to avoid duplicates)
template_http_requests_total = Counter(
    'template_http_requests_total', 'Total HTTP requests (template)', ['method', 'endpoint', 'status']
)
template_http_request_duration_seconds = Histogram(
    'template_http_request_duration_seconds', 'HTTP request duration (template)', ['method', 'endpoint']
)

# Tạo FastAPI app
app = FastAPI(
    title="Driver",
    description="Template service for microservices",
    version="1.0.0"
)

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
    template_http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    template_http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

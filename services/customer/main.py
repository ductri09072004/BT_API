from fastapi import FastAPI
from routes import router
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Tạo FastAPI app
app = FastAPI(
    title="Customer",
    description="Template service for microservices",
    version="1.0.0"
)

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

from fastapi import APIRouter, HTTPException
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

# Metrics definitions
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

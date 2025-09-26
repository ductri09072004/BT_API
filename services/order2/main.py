from fastapi import FastAPI, HTTPException, Depends, Header
from routes import router

# Tạo FastAPI app
app = FastAPI(
    title="Order2",
    description="Order2 service for microservices",
    version="1.0.0"
)

def verify_api_key(x_api_key: str = Header(..., alias="x-api-key")):
    """Middleware để verify API key cho tất cả endpoints"""
    if x_api_key != "duza-x-api-key":  # Thay đổi key này
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Health check endpoint không cần API key
@app.get("/healthz")
async def health_check():
    """Health check endpoint for Kubernetes"""
    return {"status": "ok", "service": "order2"}

# Đăng ký routes với dependency (trừ healthz)
app.include_router(router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

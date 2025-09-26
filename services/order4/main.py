from fastapi import FastAPI, HTTPException, Depends, Header
from routes import router

# Tạo FastAPI app
app = FastAPI(
    title="Template",
    description="Template service for microservices",
    version="1.0.0"
)

def verify_api_key(x_api_key: str = Header(..., alias="x-api-key")):
    """Middleware để verify API key cho tất cả endpoints"""
    if x_api_key != "duza-x-api-key":  # Thay đổi key này
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Đăng ký routes với dependency
app.include_router(router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from routes import router

# Tạo FastAPI app
app = FastAPI(
    title="User",
    description="Template service for microservices",
    version="1.0.0"
)

# Đăng ký routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

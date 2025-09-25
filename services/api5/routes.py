from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@router.get("/A")
async def hello_world():
    """Hello world endpoint"""
    return {"message": "hello world"}

# Thêm các routes khác ở đây
# @router.get("/your-endpoint")
# async def your_function():
#     return {"data": "your response"}

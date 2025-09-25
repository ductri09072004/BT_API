from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "payment"}

@router.get("/payment")
async def hello_world():
    """Hello world endpoint"""
    return {"message": "this is payment"}

# Thêm các routes khác ở đây
# @router.get("/your-endpoint")
# async def your_function():
#     return {"data": "your response"}

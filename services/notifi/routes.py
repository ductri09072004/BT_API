from fastapi import APIRouter

router = APIRouter()


@router.get("/notifi")
async def hello_world():
    """Hello world endpoint"""
    return {"message": "this is notifi v3"}

# Thêm các routes khác ở đây
# @router.get("/your-endpoint")
# async def your_function():
#     return {"data": "your response"}

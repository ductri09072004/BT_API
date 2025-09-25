from fastapi import APIRouter

router = APIRouter()


@router.get("/user")
async def user():
    """Hello world endpoint"""
    return {"message": "this is user",
            "service": "user",
            "name": "blueduck"}



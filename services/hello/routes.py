from fastapi import APIRouter

router = APIRouter()

@router.get("/A")
async def hello_world():
    """Hello world endpoint"""
    return {"message": "hello world", "service": "hello"}

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "hello"}

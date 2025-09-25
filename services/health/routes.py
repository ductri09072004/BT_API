from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "health", "version": "v2.0", "message": "Updated!"}

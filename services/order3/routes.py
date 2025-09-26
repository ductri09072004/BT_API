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

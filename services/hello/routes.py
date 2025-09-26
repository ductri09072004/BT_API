from fastapi import APIRouter, HTTPException
from db import db

router = APIRouter()


@router.get("/users")
async def list_users(skip: int = 0, limit: int = 20):
    if db is None:
        raise HTTPException(status_code=500, detail="MONGODB_URI is not configured")
    if limit <= 0:
        limit = 20
    docs = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])  # serialize ObjectId
    return {"items": docs, "count": len(docs), "skip": skip, "limit": limit}


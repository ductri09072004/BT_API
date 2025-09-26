from fastapi import APIRouter, HTTPException
from db import db

router = APIRouter()


@router.get("/orders")
async def get_orders():
    if db is None:
        raise HTTPException(status_code=500, detail="MONGODB_URI is not configured")
    docs = await db.orders.find().to_list(length=None)
    # Convert to list and serialize ObjectId
    result = []
    for doc in docs:
        doc_dict = dict(doc)
        if "_id" in doc_dict:
            doc_dict["_id"] = str(doc_dict["_id"])
        result.append(doc_dict)
    return result
    

# uvicorn main:app --reload --host 0.0.0.0 --port 8000

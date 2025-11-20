import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import create_document, get_documents, db
from schemas import Store as StoreSchema, Product as ProductSchema

app = FastAPI(title="E-commerce Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc = {**doc}
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    # Convert nested ObjectIds if any
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

# -------- Root & Health --------
@app.get("/")
def read_root():
    return {"message": "E-commerce Builder API running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# -------- E-commerce Builder: Stores --------
@app.post("/api/stores")
def create_store(store: StoreSchema):
    store_id = create_document("store", store)
    created = db["store"].find_one({"_id": ObjectId(store_id)})
    return serialize_doc(created)

@app.get("/api/stores")
def list_stores():
    docs = get_documents("store")
    return [serialize_doc(d) for d in docs]

# -------- Products --------
@app.post("/api/products")
def create_product(product: ProductSchema):
    # Ensure store exists
    store_oid = ObjectId(product.store_id) if ObjectId.is_valid(product.store_id) else None
    if not store_oid:
        raise HTTPException(status_code=400, detail="Invalid store_id")
    store = db["store"].find_one({"_id": store_oid})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    product_id = create_document("product", product)
    created = db["product"].find_one({"_id": ObjectId(product_id)})
    return serialize_doc(created)

@app.get("/api/stores/{store_id}/products")
def list_products_for_store(store_id: str):
    if not ObjectId.is_valid(store_id):
        raise HTTPException(status_code=400, detail="Invalid store_id")
    docs = get_documents("product", {"store_id": store_id})
    return [serialize_doc(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
